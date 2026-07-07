package com.root.repository;

import com.root.entity.ComponentClassification;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ComponentRepository extends JpaRepository<ComponentClassification, Integer> {
}