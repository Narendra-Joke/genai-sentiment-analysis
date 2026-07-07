package com.root.dto;

public class ComponentSentimentResponse {

    private String component;
    private long positiveCount;
    private long negativeCount;
    private long totalCount;

    private double positivePercentage;
    private double negativePercentage;

    public ComponentSentimentResponse(
            String component,
            long positiveCount,
            long negativeCount,
            long totalCount,
            double positivePercentage,
            double negativePercentage) {

        this.component = component;
        this.positiveCount = positiveCount;
        this.negativeCount = negativeCount;
        this.totalCount = totalCount;
        this.positivePercentage = positivePercentage;
        this.negativePercentage = negativePercentage;
    }

    public String getComponent() { return component; }
    public long getPositiveCount() { return positiveCount; }
    public long getNegativeCount() { return negativeCount; }
    public long getTotalCount() { return totalCount; }

    public double getPositivePercentage() { return positivePercentage; }
    public double getNegativePercentage() { return negativePercentage; }
}