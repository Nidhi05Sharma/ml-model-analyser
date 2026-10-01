package com.example.ml_analyser_backend;

import java.io.IOException;

import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api")
public class TrainController {

    private final RestClient restClient;
    private final ExperimentRepository experimentRepository;

    public TrainController(ExperimentRepository experimentRepository) {
        this.experimentRepository = experimentRepository;

        this.restClient = RestClient.builder()
                .baseUrl("http://127.0.0.1:8000")
                .build();
    }

    @PostMapping(value = "/train", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<TrainResponse> train(
            @RequestParam("file") MultipartFile file,
            @RequestParam("learning_type") String learningType,
            @RequestParam(value = "problem_type", required = false) String problemType,
            @RequestParam("model") String model) throws IOException {

        ByteArrayResource fileResource = new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return file.getOriginalFilename();
            }
        };

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();

        body.add("file", fileResource);
        body.add("learning_type", learningType);

        if (problemType != null) {
            body.add("problem_type", problemType);
        }

        body.add("model", model);

        TrainResponse response = restClient.post()
                .uri("/train")
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(body)
                .retrieve()
                .body(TrainResponse.class);

        // Save experiment in database
        Experiment experiment = new Experiment();

        experiment.setFilename(response.getFilename());
        experiment.setLearningType(response.getLearning_type());
        experiment.setProblemType(response.getProblem_type());
        experiment.setModel(response.getModel());

        Object accuracyValue = response.getResults().get("accuracy");

        if (accuracyValue != null) {
            experiment.setAccuracy(Double.valueOf(accuracyValue.toString()));
        }

        experimentRepository.save(experiment);

        return ResponseEntity.ok(response);
    }
}