package com.root.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "component_opinion_insights")
public class ComponentOpinionInsight {

    @Id
    private Long id;

    @Column(name="product_name")
    private String productName;

    @Column(name="component")
    private String component;

    @Column(name="sentiment")
    private String sentiment;

    @Column(name="sentiment_classified")
    private Integer sentimentClassified;

    @Column(name="sentiment_confidence")
    private Double sentimentConfidence;

    @Lob
    @Column(name = "content", columnDefinition = "MEDIUMTEXT")
    private String content;

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public Long getId() { return id; }

    public String getProductName() { return productName; }

    public String getComponent() { return component; }

    public String getSentiment() { return sentiment; }

    public Integer getSentimentClassified() { return sentimentClassified; }

    public Double getSentimentConfidence() { return sentimentConfidence; }
}