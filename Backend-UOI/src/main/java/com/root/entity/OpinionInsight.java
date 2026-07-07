package com.root.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "opinion_insights")
public class OpinionInsight {

    @Id
    private Integer id;

    @Column(name="product_name")
    private String productName;

    @Column(name="sentiment")
    private String sentiment;

    @Column(name="sentiment_confidence")
    private Double sentimentConfidence;

    @Column(name="sentiment_classified")
    private Integer sentimentClassified;

    @Column(name = "source")
    private String source;

    @Column(name="country")
    private String country;

    @Lob
    @Column(name = "content", columnDefinition = "MEDIUMTEXT")
    private String content;

    public String getContent() {
        return content;
    }

    public String getCountry() {
        return country;
    }

    public String getSource() {
        return source;
    }


    public Integer getId() {
        return id;
    }

    public String getProductName() {
        return productName;
    }

    public String getSentiment() {
        return sentiment;
    }

    public Double getSentimentConfidence() {
        return sentimentConfidence;
    }

    public Integer getSentimentClassified() {
        return sentimentClassified;
    }

}