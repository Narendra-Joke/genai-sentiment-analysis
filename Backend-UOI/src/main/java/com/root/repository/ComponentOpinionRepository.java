package com.root.repository;

import com.root.entity.ComponentOpinionInsight;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ComponentOpinionRepository
        extends JpaRepository<ComponentOpinionInsight, Long> {

    @Query("""
        SELECT o FROM ComponentOpinionInsight o
        WHERE o.component = :component
        AND o.sentimentClassified = 1
        AND o.sentiment IN ('positive','negative')
    """)
    List<ComponentOpinionInsight> findComponentReviews(
            @Param("component") String component);

    @Query("""
    SELECT o FROM ComponentOpinionInsight o
    WHERE o.productName = :productName
    AND o.component = :component
    AND o.sentimentClassified = 1
    AND o.sentiment IN ('positive','negative')
    """)
    List<ComponentOpinionInsight> findReviewsByProductAndComponent(
            @Param("productName") String productName,
            @Param("component") String component);

    // chatbot methods
    @Query("""
    SELECT c.content
    FROM ComponentOpinionInsight c
    WHERE LOWER(c.productName) LIKE LOWER(CONCAT('%', :product, '%'))
    AND LOWER(c.component) = LOWER(:component)
    AND c.sentimentClassified = 1
    """)
    List<String> fetchReviews(String product, String component);

    // ✅ POSITIVE
    @Query("""
        SELECT c.content
        FROM ComponentOpinionInsight c
        WHERE LOWER(c.productName) LIKE LOWER(CONCAT('%', :product, '%'))
        AND LOWER(c.component) = LOWER(:component)
        AND c.sentiment = 'positive'
        AND c.sentimentClassified = 1
        AND c.sentimentConfidence >= :confidence
        ORDER BY c.sentimentConfidence DESC
    """)
    List<String> fetchTopPositiveReviews(
            String product,
            String component,
            Double confidence,
            Pageable pageable
    );

    // ✅ NEGATIVE
    @Query("""
        SELECT c.content
        FROM ComponentOpinionInsight c
        WHERE LOWER(c.productName) LIKE LOWER(CONCAT('%', :product, '%'))
        AND LOWER(c.component) = LOWER(:component)
        AND c.sentiment = 'negative'
        AND c.sentimentClassified = 1
        AND c.sentimentConfidence >= :confidence
        ORDER BY c.sentimentConfidence DESC
    """)
    List<String> fetchTopNegativeReviews(
            String product,
            String component,
            Double confidence,
            Pageable pageable
    );

    // ✅ MIXED
    @Query("""
        SELECT c.content
        FROM ComponentOpinionInsight c
        WHERE LOWER(c.productName) LIKE LOWER(CONCAT('%', :product, '%'))
        AND LOWER(c.component) = LOWER(:component)
        AND c.sentimentClassified = 1
        ORDER BY c.sentimentConfidence DESC
    """)
    List<String> fetchMixedReviews(
            String product,
            String component,
            Pageable pageable
    );

    @Query("""
    SELECT c.productName, c.content, c.sentiment, c.sentimentConfidence
    FROM ComponentOpinionInsight c
    WHERE LOWER(c.component) = LOWER(:component)
    AND c.sentimentClassified = 1
    AND c.sentimentConfidence >= :confidence
    ORDER BY c.sentimentConfidence DESC
    """)
    List<Object[]> fetchTopReviewsByComponentAcrossProducts(
            String component,
            Double confidence,
            Pageable pageable
    );

}