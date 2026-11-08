

#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <unistd.h>

static int send_acknowledgment(int client_fd) {
    static const char acknowledgment[] = "OK\n";
    size_t sent = 0;
    while (sent < sizeof(acknowledgment) - 1) {
        ssize_t result = send(
            client_fd,
            acknowledgment + sent,
            sizeof(acknowledgment) - 1 - sent,
            0
        );
        if (result < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("sending acknowledgment failed");
            return -1;
        }
        if (result == 0) {
            errno = EPIPE;
            perror("sending acknowledgment");
            return -1;
        }
        sent += (size_t)result;
    }

    return 0;
}

static int parse_port(const char *value, unsigned short *port) {
    char *end;
    long parsed = strtol(value, &end, 10);
    if (*value == '\0' || *end != '\0' || parsed < 0 || parsed > 65535) {
        return -1;
    }

    *port = (unsigned short)parsed;
    return 0;
}

static int handle_client(int client_fd) {
    FILE *stream = fdopen(client_fd, "r");
    if (stream == NULL) {
        perror("fdopen");
        close(client_fd);
        return -1;
    }

    char *line = NULL;
    size_t capacity = 0;
    ssize_t length;
    while ((length = getline(&line, &capacity, stream)) != -1) {
        if (length > 0 && line[length - 1] == '\n') {
            line[--length] = '\0';
        }
        if (length > 0 && line[length - 1] == '\r') {
            line[--length] = '\0';
        }

        if (printf("%s\n", line) < 0 || fflush(stdout) == EOF) {
            perror("writing received message");
            free(line);
            fclose(stream);
            return -1;
        }

        if (send_acknowledgment(client_fd) != 0) {
            free(line);
            fclose(stream);
            return -1;
        }
    }

    if (ferror(stream)) {
        perror("reading client message");
        free(line);
        fclose(stream);
        return -1;
    }

    free(line);
    fclose(stream);
    return 0;
}

int main(int argc, char **argv) {
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR) {
        perror("ignoring SIGPIPE");
        return EXIT_FAILURE;
    }

    unsigned short port = 8080;
    if (argc > 2 || (argc == 2 && parse_port(argv[1], &port) != 0)) {
        fprintf(stderr, "Usage: %s [port (0-65535)]\n", argv[0]);
        return EXIT_FAILURE;
    }

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    struct sockaddr_in address = {0};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    address.sin_port = htons(port);

    if (bind(server_fd, (const struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind");
        close(server_fd);
        return EXIT_FAILURE;
    }

    socklen_t address_length = sizeof(address);
    if (getsockname(server_fd, (struct sockaddr *)&address, &address_length) < 0) {
        perror("getsockname");
        close(server_fd);
        return EXIT_FAILURE;
    }

    if (listen(server_fd, 5) < 0) {
        perror("listen");
        int result = close(server_fd);

        if (result < 0) {
            perror("close after listen failure");
        }
        return EXIT_FAILURE;
    }

    printf("Listening on 127.0.0.1:%u\n", ntohs(address.sin_port));
    fflush(stdout);

    for (;;) {
        int client_fd = accept(server_fd, NULL, NULL);
        if (client_fd < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("accept");
            close(server_fd);
            return EXIT_FAILURE;
        }

        if (handle_client(client_fd) != 0) {
            close(server_fd);
            return EXIT_FAILURE;
        }
    }
}