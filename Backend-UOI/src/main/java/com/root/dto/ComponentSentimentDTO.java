package com.root.dto;

public class ComponentSentimentDTO {

    private int positiveCount;
    private int negativeCount;
    private int totalCount;
    private double positivePercentage;
    private double negativePercentage;

    public ComponentSentimentDTO(int positiveCount, int negativeCount) {

        this.positiveCount = positiveCount;
        this.negativeCount = negativeCount;
        this.totalCount = positiveCount + negativeCount;

        if(totalCount > 0){
            double pos = (positiveCount * 100.0) / totalCount;
            double neg = (negativeCount * 100.0) / totalCount;

            this.positivePercentage = Math.round(pos * 100.0) / 100.0;
            this.negativePercentage = Math.round(neg * 100.0) / 100.0;
        }
    }

    public int getPositiveCount() { return positiveCount; }
    public int getNegativeCount() { return negativeCount; }
    public int getTotalCount() { return totalCount; }
    public double getPositivePercentage() { return positivePercentage; }
    public double getNegativePercentage() { return negativePercentage; }
}