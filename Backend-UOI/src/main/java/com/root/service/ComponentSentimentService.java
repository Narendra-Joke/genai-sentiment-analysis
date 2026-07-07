package com.root.service;

import com.root.dto.ComponentSentimentResponse;
import com.root.entity.ComponentClassification;
import com.root.entity.ComponentOpinionInsight;
import com.root.repository.ComponentOpinionRepository;
import com.root.repository.ComponentRepository;

import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ComponentSentimentService {

    private final ComponentRepository componentRepository;
    private final ComponentOpinionRepository opinionRepository;

    public ComponentSentimentService(
            ComponentRepository componentRepository,
            ComponentOpinionRepository opinionRepository) {

        this.componentRepository = componentRepository;
        this.opinionRepository = opinionRepository;
    }

    public ComponentSentimentResponse getComponentSentiment(int componentId) {

        ComponentClassification component =
                componentRepository.findById(componentId)
                        .orElseThrow();

        String componentName = component.getComponent();

        List<ComponentOpinionInsight> reviews =
                opinionRepository.findComponentReviews(componentName);

        long positive = reviews.stream()
                .filter(r -> r.getSentiment().equals("positive"))
                .count();

        long negative = reviews.stream()
                .filter(r -> r.getSentiment().equals("negative"))
                .count();

        long total = positive + negative;

        double positivePerc = total == 0 ? 0 :
                (positive * 100.0) / total;

        double negativePerc = total == 0 ? 0 :
                (negative * 100.0) / total;

        positivePerc = Math.round(positivePerc * 100.0) / 100.0;
        negativePerc = Math.round(negativePerc * 100.0) / 100.0;

        return new ComponentSentimentResponse(
                component.getComponent(),
                positive,
                negative,
                total,
                positivePerc,
                negativePerc
        );
    }
}