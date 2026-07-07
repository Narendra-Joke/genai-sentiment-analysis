package com.root.service;

import com.root.dto.ComponentSentimentDTO;
import com.root.dto.ProductDashboardDTO;
import com.root.dto.SourceSentimentDTO;
import com.root.entity.ComponentClassification;
import com.root.entity.ComponentOpinionInsight;
import com.root.entity.OpinionInsight;
import com.root.entity.Product;
import com.root.repository.ComponentOpinionRepository;
import com.root.repository.ComponentRepository;
import com.root.repository.OpinionInsightRepository;
import com.root.repository.ProductRepository;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class DashboardService {

    private final ProductRepository productRepository;
    private final OpinionInsightRepository opinionRepository;

    private final ComponentRepository componentRepository;
    private final ComponentOpinionRepository componentOpinionRepository;

    public DashboardService(
            ProductRepository productRepository,
            OpinionInsightRepository opinionRepository,
            ComponentRepository componentRepository,
            ComponentOpinionRepository componentOpinionRepository
    ){
        this.productRepository = productRepository;
        this.opinionRepository = opinionRepository;
        this.componentRepository = componentRepository;
        this.componentOpinionRepository = componentOpinionRepository;
    }

    public ProductDashboardDTO getDashboard(Integer productId){

        Product product =
                productRepository.findById(productId)
                        .orElseThrow();

        List<OpinionInsight> reviews =
                opinionRepository.findSentimentReviews(product.getProductName());

        int positive = 0;
        int negative = 0;

        for(OpinionInsight r : reviews){

            if("positive".equalsIgnoreCase(r.getSentiment())){
                positive++;
            }
            else if("negative".equalsIgnoreCase(r.getSentiment())){
                negative++;
            }
        }

        int total = positive + negative;

        double positivePercent = 0;
        double negativePercent = 0;

        if(total > 0){
            positivePercent = (positive * 100.0) / total;
            negativePercent = (negative * 100.0) / total;

            positivePercent = Math.round(positivePercent * 100.0) / 100.0;
            negativePercent = Math.round(negativePercent * 100.0) / 100.0;
        }

        ProductDashboardDTO dto = new ProductDashboardDTO();

        dto.setProductName(product.getProductName());
        dto.setProductImage(product.getProductImage());
        dto.setReleasedDate(product.getReleasedDate().toString());
        dto.setChipset(product.getChipset());
        dto.setMemory(product.getMemory());
        dto.setCamera(product.getCamera());
        dto.setBattery(product.getBattery());

        dto.setTotalCount(total);
        dto.setPositiveReviewCount(positive);
        dto.setNegativeReviewCount(negative);

        dto.setPositivePercentage(positivePercent);
        dto.setNegativePercentage(negativePercent);

        return dto;
    }

    public Map<String, ComponentSentimentDTO> getComponentSentiment(Integer productId){

        Product product = productRepository.findById(productId).orElseThrow();

        String productName = product.getProductName();

        List<ComponentClassification> components = componentRepository.findAll();

        Map<String, ComponentSentimentDTO> response = new HashMap<>();

        for(ComponentClassification c : components){

            String component = c.getComponent();

            List<ComponentOpinionInsight> reviews =
                    componentOpinionRepository
                            .findReviewsByProductAndComponent(productName, component);

            int positive = 0;
            int negative = 0;

            for(ComponentOpinionInsight r : reviews){

                if("positive".equalsIgnoreCase(r.getSentiment())){
                    positive++;
                }
                else if("negative".equalsIgnoreCase(r.getSentiment())){
                    negative++;
                }
            }

            response.put(component, new ComponentSentimentDTO(positive, negative));
        }

        return response;
    }

//    public Map<String, SourceSentimentDTO> getSourceSentiment(Integer productId){
//
//        Product product = productRepository.findById(productId).orElseThrow();
//
//        String productName = product.getProductName();
//
//        List<OpinionInsight> reviews =
//                opinionRepository.findSourceReviews(productName);
//
//        Map<String, Integer> positiveMap = new HashMap<>();
//        Map<String, Integer> negativeMap = new HashMap<>();
//
//        for(OpinionInsight r : reviews){
//
//            String source = r.getSource();
//
//            if("positive".equalsIgnoreCase(r.getSentiment())){
//                positiveMap.put(source,
//                        positiveMap.getOrDefault(source,0) + 1);
//            }
//            else if("negative".equalsIgnoreCase(r.getSentiment())){
//                negativeMap.put(source,
//                        negativeMap.getOrDefault(source,0) + 1);
//            }
//        }
//
//        Map<String, SourceSentimentDTO> response = new HashMap<>();
//
//        for(String source : positiveMap.keySet()){
//
//            int positive = positiveMap.getOrDefault(source,0);
//            int negative = negativeMap.getOrDefault(source,0);
//
//            int total = positive + negative;
//
//            double positivePercent = 0;
//            double negativePercent = 0;
//
//            if(total > 0){
//                positivePercent = (positive * 100.0) / total;
//                negativePercent = (negative * 100.0) / total;
//
//                positivePercent = Math.round(positivePercent * 100.0) / 100.0;
//                negativePercent = Math.round(negativePercent * 100.0) / 100.0;
//            }
//
//            SourceSentimentDTO dto =
//                    new SourceSentimentDTO(
//                            positive,
//                            negative,
//                            total,
//                            positivePercent,
//                            negativePercent
//                    );
//
//            response.put(source,dto);
//        }
//
//        return response;
//    }

    public Map<String, SourceSentimentDTO> getSourceSentiment(Integer productId){

        Product product = productRepository.findById(productId).orElseThrow();

        String productName = product.getProductName();

        List<OpinionInsight> reviews =
                opinionRepository.findSourceReviews(productName);

        Map<String, Integer> positiveMap = new HashMap<>();
        Map<String, Integer> negativeMap = new HashMap<>();

        for(OpinionInsight r : reviews){

            String source = r.getSource();

            if("positive".equalsIgnoreCase(r.getSentiment())){
                positiveMap.put(source,
                        positiveMap.getOrDefault(source,0) + 1);
            }
            else if("negative".equalsIgnoreCase(r.getSentiment())){
                negativeMap.put(source,
                        negativeMap.getOrDefault(source,0) + 1);
            }
        }

        Map<String, SourceSentimentDTO> tempMap = new HashMap<>();

        // collect all sources
        java.util.Set<String> sources = new java.util.HashSet<>();
        sources.addAll(positiveMap.keySet());
        sources.addAll(negativeMap.keySet());

        for(String source : sources){

            int positive = positiveMap.getOrDefault(source,0);
            int negative = negativeMap.getOrDefault(source,0);

            int total = positive + negative;

            double positivePercent = 0;
            double negativePercent = 0;

            if(total > 0){
                positivePercent = (positive * 100.0) / total;
                negativePercent = (negative * 100.0) / total;

                positivePercent = Math.round(positivePercent * 100.0) / 100.0;
                negativePercent = Math.round(negativePercent * 100.0) / 100.0;
            }

            SourceSentimentDTO dto =
                    new SourceSentimentDTO(
                            positive,
                            negative,
                            total,
                            positivePercent,
                            negativePercent
                    );

            tempMap.put(source,dto);
        }

        // sort by totalCount and return top 5
        Map<String, SourceSentimentDTO> response =
                tempMap.entrySet()
                        .stream()
                        .sorted((a,b) ->
                                Integer.compare(
                                        b.getValue().getTotalCount(),
                                        a.getValue().getTotalCount()
                                ))
                        .limit(5)
                        .collect(
                                java.util.stream.Collectors.toMap(
                                        Map.Entry::getKey,
                                        Map.Entry::getValue,
                                        (a,b)->a,
                                        java.util.LinkedHashMap::new
                                )
                        );

        return response;
    }

    public Map<String, Integer> getCountryReviewCounts(Integer productId){

        Product product = productRepository.findById(productId).orElseThrow();

        String productName = product.getProductName();

        List<Object[]> results =
                opinionRepository.findCountryReviewCounts(productName);

        Map<String, Integer> response = new HashMap<>();

        int limit = Math.min(results.size(),5);

        for(int i=0;i<limit;i++){

            Object[] row = results.get(i);

            String country = (String) row[0];
            Long count = (Long) row[1];

            response.put(country, count.intValue());
        }

        return response;
    }
}
