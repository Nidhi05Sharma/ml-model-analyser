package com.example.ml_analyser_backend;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;

@RestController
public class FastApiTestController {

    private final RestClient restClient;

    public FastApiTestController() {
        this.restClient = RestClient.builder()
                .baseUrl("http://127.0.0.1:8000")
                .build();
    }

    @GetMapping("/api/fastapi-test")
    public String testFastApi() {

        return restClient.get()
                .uri("/")
                .retrieve()
                .body(String.class);
    }
}