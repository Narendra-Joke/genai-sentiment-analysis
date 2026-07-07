package com.root.repository;

import com.root.entity.OpinionInsight;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface OpinionInsightRepository
        extends JpaRepository<OpinionInsight,Integer> {

    @Query("""
    SELECT o FROM OpinionInsight o
    WHERE o.productName = :productName
    AND o.sentimentClassified = 1
    AND o.sentiment IN ('positive','negative')
    """)
    List<OpinionInsight> findSentimentReviews(
            @Param("productName") String productName
    );

    @Query("""
    SELECT o FROM OpinionInsight o
    WHERE o.productName = :productName
    AND o.sentimentClassified = 1
    AND o.sentiment IN ('positive','negative')
    """)
    List<OpinionInsight> findSourceReviews(
            @Param("productName") String productName
    );

    @Query("""
    SELECT o.country, COUNT(o)
    FROM OpinionInsight o
    WHERE o.productName = :productName
    AND o.sentimentClassified = 1
    GROUP BY o.country
    ORDER BY COUNT(o) DESC
    """)
    List<Object[]> findCountryReviewCounts(
            @Param("productName") String productName
    );

    // chatbot methods
    @Query("""
    SELECT o.content
    FROM OpinionInsight o
    WHERE LOWER(o.productName) LIKE LOWER(CONCAT('%', :product, '%'))
    AND o.sentimentClassified = 1
""")
    List<String> fetchReviews(String product);


    @Query("SELECT DISTINCT o.productName FROM OpinionInsight o")
    List<String> findDistinctProducts();

    // ✅ POSITIVE
    @Query("""
        SELECT o.content
        FROM OpinionInsight o
        WHERE LOWER(o.productName) LIKE LOWER(CONCAT('%', :product, '%'))
        AND o.sentiment = 'positive'
        AND o.sentimentClassified = 1
        AND o.sentimentConfidence >= :confidence
        ORDER BY o.sentimentConfidence DESC
    """)
    List<String> fetchTopPositiveReviews(
            String product,
            Double confidence,
            Pageable pageable
    );

    // ✅ NEGATIVE
    @Query("""
        SELECT o.content
        FROM OpinionInsight o
        WHERE LOWER(o.productName) LIKE LOWER(CONCAT('%', :product, '%'))
        AND o.sentiment = 'negative'
        AND o.sentimentClassified = 1
        AND o.sentimentConfidence >= :confidence
        ORDER BY o.sentimentConfidence DESC
    """)
    List<String> fetchTopNegativeReviews(
            String product,
            Double confidence,
            Pageable pageable
    );

    // ✅ MIXED
    @Query("""
        SELECT o.content
        FROM OpinionInsight o
        WHERE LOWER(o.productName) LIKE LOWER(CONCAT('%', :product, '%'))
        AND o.sentimentClassified = 1
        ORDER BY o.sentimentConfidence DESC
    """)
    List<String> fetchMixedReviews(
            String product,
            Pageable pageable
    );
}