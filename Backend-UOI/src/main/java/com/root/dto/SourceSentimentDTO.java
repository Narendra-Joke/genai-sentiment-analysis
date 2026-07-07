package com.root.dto;

public class SourceSentimentDTO {

    private int positiveCount;
    private int negativeCount;
    private int totalCount;

    private double positivePercentage;
    private double negativePercentage;

    public SourceSentimentDTO(){}

    public SourceSentimentDTO(int positiveCount,int negativeCount,
                              int totalCount,
                              double positivePercentage,
                              double negativePercentage){
        this.positiveCount = positiveCount;
        this.negativeCount = negativeCount;
        this.totalCount = totalCount;
        this.positivePercentage = positivePercentage;
        this.negativePercentage = negativePercentage;
    }

    public int getPositiveCount() {
        return positiveCount;
    }

    public void setPositiveCount(int positiveCount) {
        this.positiveCount = positiveCount;
    }

    public int getNegativeCount() {
        return negativeCount;
    }

    public void setNegativeCount(int negativeCount) {
        this.negativeCount = negativeCount;
    }

    public int getTotalCount() {
        return totalCount;
    }

    public void setTotalCount(int totalCount) {
        this.totalCount = totalCount;
    }

    public double getPositivePercentage() {
        return positivePercentage;
    }

    public void setPositivePercentage(double positivePercentage) {
        this.positivePercentage = positivePercentage;
    }

    public double getNegativePercentage() {
        return negativePercentage;
    }

    public void setNegativePercentage(double negativePercentage) {
        this.negativePercentage = negativePercentage;
    }
}