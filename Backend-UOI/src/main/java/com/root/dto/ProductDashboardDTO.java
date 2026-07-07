package com.root.dto;

public class ProductDashboardDTO {

    private String productName;
    private String productImage;
    private String releasedDate;
    private String chipset;
    private String memory;
    private String camera;
    private String battery;

    private int totalCount;
    private int positiveReviewCount;
    private int negativeReviewCount;

    private double positivePercentage;
    private double negativePercentage;

    // getters setters

    public String getProductName() {
        return productName;
    }

    public void setProductName(String productName) {
        this.productName = productName;
    }

    public String getProductImage() {
        return productImage;
    }

    public void setProductImage(String productImage) {
        this.productImage = productImage;
    }

    public String getReleasedDate() {
        return releasedDate;
    }

    public void setReleasedDate(String releasedDate) {
        this.releasedDate = releasedDate;
    }

    public String getChipset() {
        return chipset;
    }

    public void setChipset(String chipset) {
        this.chipset = chipset;
    }

    public String getMemory() {
        return memory;
    }

    public void setMemory(String memory) {
        this.memory = memory;
    }

    public String getCamera() {
        return camera;
    }

    public void setCamera(String camera) {
        this.camera = camera;
    }

    public String getBattery() {
        return battery;
    }

    public void setBattery(String battery) {
        this.battery = battery;
    }

    public int getTotalCount() {
        return totalCount;
    }

    public void setTotalCount(int totalCount) {
        this.totalCount = totalCount;
    }

    public int getPositiveReviewCount() {
        return positiveReviewCount;
    }

    public void setPositiveReviewCount(int positiveReviewCount) {
        this.positiveReviewCount = positiveReviewCount;
    }

    public int getNegativeReviewCount() {
        return negativeReviewCount;
    }

    public void setNegativeReviewCount(int negativeReviewCount) {
        this.negativeReviewCount = negativeReviewCount;
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