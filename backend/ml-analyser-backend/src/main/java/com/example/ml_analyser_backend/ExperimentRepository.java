
package com.example.ml_analyser_backend;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ExperimentRepository extends JpaRepository<Experiment, Long> {

    List<Experiment> findByFilename(String filename);
}
