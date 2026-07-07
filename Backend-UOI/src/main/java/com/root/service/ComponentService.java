package com.root.service;

import com.root.entity.ComponentClassification;
import com.root.repository.ComponentRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ComponentService {

    private final ComponentRepository componentRepository;

    public ComponentService(ComponentRepository componentRepository) {
        this.componentRepository = componentRepository;
    }

    public List<ComponentClassification> getAllComponents() {
        return componentRepository.findAll();
    }
}