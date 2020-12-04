//
// Created by 1di0t on 12/4/20.
//

#include <curl/curl.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>


#define MAX_THREAD_COUNT 100
#define MAX_PAGE_COUNT 812
#define BASE_REQUEST_MOVIE_URL "http://www.y80s.com/movie/list/-----p"

struct curl_string {
    char *ptr;
    size_t len;
};

void init_string(struct curl_string *s) {
    s->len = 0;
    s->ptr = malloc(s->len + 1);
    if (s->ptr == NULL) {
        fprintf(stderr, "malloc() failed\n");
        exit(EXIT_FAILURE);
    }
    s->ptr[0] = '\0';
}

size_t write_func(void *ptr, size_t size, size_t nmemb, struct curl_string *s) {
    size_t new_len = s->len + size * nmemb;
    s->ptr = realloc(s->ptr, new_len + 1);
    if (s->ptr == NULL) {
        fprintf(stderr, "realloc() failed\n");
        exit(EXIT_FAILURE);
    }
    memcpy(s->ptr + s->len, ptr, size * nmemb);
    s->ptr[new_len] = '\0';
    s->len = new_len;

    return size * nmemb;
}


static void *get_request(void *request_url) {

    CURL *curl;
    CURLcode res;
    struct curl_string s;
    init_string(&s);

    struct curl_slist *headers = NULL;

    headers = curl_slist_append(headers, "User-Agent: Mozilla/5.0 (X11; Fedora; Linux x86_64) "
                                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36");
    headers = curl_slist_append(headers, "Content-Type: text/html; charset=utf-8");

    curl = curl_easy_init();

    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_URL, request_url);

    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_func);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &s);

    res = curl_easy_perform(curl);
    if (res != CURLE_OK) {
        fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
    }

    printf("%s\n", s.ptr);
    free(s.ptr);

    curl_easy_cleanup(curl);
    return 0;
}


int main(int argc, char **argv) {
    pthread_t tid[MAX_THREAD_COUNT];

    char base_request_url[40];

    strcpy(base_request_url, BASE_REQUEST_MOVIE_URL);
    int i;

    for (i = 0; i < MAX_THREAD_COUNT; i++) {
        char current_req_url[50];
        sprintf(current_req_url, "%s%d", base_request_url, i + 1);

        char *current_url = current_req_url;

        int error = pthread_create(&tid[i], NULL, get_request, current_url);
        if (0 != error)
            fprintf(stderr, "Couldn't run thread number %d, errno %d\n", i, error);
        else
            fprintf(stderr, "Thread %d, gets %s\n", i, current_url);
    }

    for (i = 0; i < MAX_THREAD_COUNT; i++) {
        pthread_join(tid[i], NULL);
        fprintf(stderr, "Thread %d terminated\n", i);
    }
    curl_global_cleanup();
    return 0;
}
