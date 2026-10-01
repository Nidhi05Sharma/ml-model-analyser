package com.example.ml_analyser_backend;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ExperimentController {

    private final ExperimentRepository experimentRepository;

    public ExperimentController(ExperimentRepository experimentRepository) {
        this.experimentRepository = experimentRepository;
    }

    @GetMapping("/api/test-db")
    public String testDatabase() {

        Experiment experiment = new Experiment();

        experiment.setFilename("test.csv");
        experiment.setLearningType("supervised");
        experiment.setProblemType("classification");
        experiment.setModel("logistic_regression");

        experimentRepository.save(experiment);

        return "Experiment saved to Supabase";
    }

    @GetMapping("/api/experiments")
    public List<Experiment> getExperiments(
            @RequestParam String filename) {

        return experimentRepository.findByFilename(filename);
    }
}

