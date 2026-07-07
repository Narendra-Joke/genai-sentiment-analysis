package com.root.service;

import com.root.repository.ComponentOpinionRepository;
import com.root.repository.OpinionInsightRepository;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.function.Supplier;

@Service
public class ChatService {

    private final ChatClient chatClient;
    private final OpinionInsightRepository opinionRepo;
    private final ComponentOpinionRepository componentRepo;

    private static final List<String> COMPONENTS =
            List.of("camera","battery","display","design","performance","audio");

    public ChatService(ChatClient chatClient,
                       OpinionInsightRepository opinionRepo,
                       ComponentOpinionRepository componentRepo) {
        this.chatClient = chatClient;
        this.opinionRepo = opinionRepo;
        this.componentRepo = componentRepo;
    }

    /* =========================================================
       MAIN METHOD
       ========================================================= */
    public String handleQuestion(String question){

        if(question == null || question.isBlank()){
            return getIntro();
        }

        String lowerQ = question.toLowerCase();

        if(isGreeting(lowerQ)){
            return getIntro();
        }

        // =========================
        // STEP 1: DETECTION
        // =========================
        String component = detectComponent(lowerQ);
        String product = findBestMatchingProduct(lowerQ);

        boolean hasProduct = product != null && !product.isBlank();
        boolean hasComponent = component != null && !component.isBlank();
        boolean isComparisonQuery = !hasProduct && hasComponent;

        if(!hasProduct && !hasComponent){
            return """
                I couldn't find the specified product or component data.

                Try:
                • Moto Edge 60 Pro camera quality
                • Pros of Moto G Stylus 2024
                """;
        }

        boolean isPros = isPros(lowerQ);
        boolean isCons = isCons(lowerQ);

        Pageable top2000 = PageRequest.of(0, 2000);
        Pageable top5000 = PageRequest.of(0, 5000);
        Pageable top1000 = PageRequest.of(0, 1000);

        List<String> reviews;

        // =========================
        // FLOW 1: COMPARISON MODE
        // =========================
        if (isComparisonQuery) {
            reviews = handleComparison(component, top1000);
        }

        // =========================
        // FLOW 2: NORMAL MODE
        // =========================
        else {
            reviews = fetchReviews(product, component, isPros, isCons, top2000, top5000);
        }

        if (reviews == null || reviews.isEmpty()) {
            return "No review data found.";
        }

        // =========================
        // CONTEXT BUILD
        // =========================
        String context = String.join("\n", reviews.stream().limit(30).toList());

        String productLine =
                (hasProduct) ? "Product: " + product : "";

        String componentLine =
                (hasComponent) ? "Component: " + component : "";

        // =========================
        // LLM CALL
        // =========================
        return safeLLMCall(() ->
                chatClient.prompt()
                        .system(SYSTEM_PROMPT)
                        .user("""
                        Question: %s
                        
                        %s
                        %s
                        
                        Reviews:
                        %s
                        """.formatted(question, productLine, componentLine, context))
                        .call()
                        .content()
        );
    }

    /* =========================================================
       FETCH LOGIC (NO DUPLICATION)
       ========================================================= */
    private List<String> fetchReviews(String product,
                                      String component,
                                      boolean isPros,
                                      boolean isCons,
                                      Pageable top2000,
                                      Pageable top5000) {

        boolean hasComponent = component != null && !component.isBlank();

        if (hasComponent) {
            if (isPros) {
                return componentRepo.fetchTopPositiveReviews(product, component, 0.80, top2000);
            } else if (isCons) {
                return componentRepo.fetchTopNegativeReviews(product, component, 0.80, top2000);
            } else {
                return componentRepo.fetchMixedReviews(product, component, top5000);
            }
        } else {
            if (isPros) {
                return opinionRepo.fetchTopPositiveReviews(product, 0.80, top2000);
            } else if (isCons) {
                return opinionRepo.fetchTopNegativeReviews(product, 0.80, top2000);
            } else {
                return opinionRepo.fetchMixedReviews(product, top5000);
            }
        }
    }

    /* =========================================================
       COMPARISON LOGIC
       ========================================================= */
    private List<String> handleComparison(String component, Pageable top1000) {

        List<Object[]> rows =
                componentRepo.fetchTopReviewsByComponentAcrossProducts(component, 0.80, top1000);

        Map<String, Double> scoreMap = new HashMap<>();

        for (Object[] row : rows) {
            String productName = (String) row[0];
            String sentiment = (String) row[2];
            Double confidence = (Double) row[3];

            double score = sentiment.equalsIgnoreCase("positive") ? confidence : -confidence;

            scoreMap.put(productName,
                    scoreMap.getOrDefault(productName, 0.0) + score);
        }

        List<String> topProducts = scoreMap.entrySet()
                .stream()
                .sorted((a, b) -> Double.compare(b.getValue(), a.getValue()))
                .limit(3)
                .map(Map.Entry::getKey)
                .toList();

        List<String> reviews = new ArrayList<>();

        for (String p : topProducts) {
            reviews.addAll(
                    componentRepo.fetchTopPositiveReviews(p, component, 0.80, PageRequest.of(0, 200))
            );
        }

        return reviews;
    }

    /* =========================================================
       HELPERS
       ========================================================= */

    private String detectComponent(String q){
        for(String c : COMPONENTS){
            if(q.contains(c)){
                return c;
            }
        }
        return null;
    }

    private boolean isGreeting(String q){
        return q.contains("hi") || q.contains("hello") || q.contains("hey");
    }

    private boolean isPros(String lowerQ){
        return lowerQ.contains("pro") || lowerQ.contains("positive") || lowerQ.contains("good")
                || lowerQ.contains("pros") || lowerQ.contains("positives") || lowerQ.contains("advantages")
                || lowerQ.contains("advantage") || lowerQ.contains("best") || lowerQ.contains("like about")
                || lowerQ.contains("love about") || lowerQ.contains("what's good about")
                || lowerQ.contains("what do you like about")
                || lowerQ.contains("what's good with") || lowerQ.contains("what do you like with")
                || lowerQ.contains("strengths") || lowerQ.contains("strong points")
                || lowerQ.contains("strong point") || lowerQ.contains("positively")|| lowerQ.contains("what's good in");
    }

    private boolean isCons(String lowerQ){
        return lowerQ.contains("cons") || lowerQ.contains("negative") || lowerQ.contains("bad")
                || lowerQ.contains("con") || lowerQ.contains("negatives") || lowerQ.contains("disadvantages")
                || lowerQ.contains("disadvantage") || lowerQ.contains("worst") || lowerQ.contains("don't like about")
                || lowerQ.contains("hate about") || lowerQ.contains("issues with") || lowerQ.contains("problems with")
                || lowerQ.contains("problem with") || lowerQ.contains("issue with") || lowerQ.contains("what's bad about")
                || lowerQ.contains("what do you dislike about")
                || lowerQ.contains("weak point") || lowerQ.contains("weak points") || lowerQ.contains("negatively")
                || lowerQ.contains("what's bad in") || lowerQ.contains("what do you dislike");
    }

    private String getIntro(){
        return """
        Hi, I'm here to help you with user reviews and opinions.
                                                      
        Try asking things like:
                                                      
        • What are the pros of Edge 70 Fusion?
        • How is the camera on Moto Edge 60 Pro?
        • Which Motorola phone has the best battery life?
        • Tell me about display quality of Moto Signature.
        """;
    }

    private String findBestMatchingProduct(String question){

        List<String> allProducts = opinionRepo.findDistinctProducts();

        String bestMatch = null;
        double bestScore = 0.0;

        for(String p : allProducts){

            String normalized = p.toLowerCase();

            if(question.contains(normalized)){
                return p;
            }

            String[] words = normalized.split(" ");
            int matchCount = 0;

            for(String w : words){
                if(question.contains(w)){
                    matchCount++;
                }
            }

            double score = (double) matchCount / words.length;

            if(score > bestScore){
                bestScore = score;
                bestMatch = p;
            }
        }

        return bestScore >= 0.7 ? bestMatch : null;
    }

    private String safeLLMCall(Supplier<String> call){
        try{
            return call.get();
        }catch(Exception e){
            e.printStackTrace();
            return "Something went wrong.";
        }
    }

    /* =========================================================
       SYSTEM PROMPT
       ========================================================= */
    private static final String SYSTEM_PROMPT1 = """
    You are a product review assistant.
    
    - Answer ONLY from given reviews
    - Mention product name
    - Mention component only if valid
    
    If pros → max 5 positives  
    If cons → max 5 negatives  
    If general → max 3 positives + 3 negatives
    
    Be concise. No hallucination.
    """;

    private static final String SYSTEM_PROMPT = """
                        You are a product review assistant.

            Your task: Summarize user reviews of a product into a clear, structured format.

            Rules:
            - Answer ONLY from the given reviews.
            - Always mention the product name.
            - Mention the component ONLY if the question is component-specific AND a valid component exists.
            - If component is null, empty, or irrelevant → DO NOT mention component.
            - Responses must be concise, bullet-pointed, and well-formatted. No long paragraphs.

            Response Logic:
            1. If the user asks for positives/pros/good:
               - Show ONLY positive points.
               - Maximum 5 bullet points.

            2. If the user asks for negatives/cons/bad:
               - Show ONLY negative points.
               - Maximum 5 bullet points.

            3. If the user asks a general review (e.g., "how is", "review", "performance"):
               - Show BOTH positives and negatives.
               - Maximum 3 positives + 3 negatives.

            4. Even if only one review exists:
               - Extract and show available positives/negatives.
               - Do NOT say "Not enough information."

            5. Do NOT add information outside reviews.
            6. Do NOT hallucinate or assume anything.

            Output Format:
            - If user asks generally (review, performance, how is, overall):
              Product: <product name>
              Component: <component (if applicable)>
                        
              Top Likes:
              - ...
              - ...
                        
              Top Dislikes:
              - ...
              - ...
              
            - If user asks for positives/pros/good/advantages:
              Product: <product name>
              Component: <component (if applicable)>
                          
              Top Likes:
              - ...
              - ...
                          
            - If user asks for negatives/cons/bad/disadvantages:
              Product: <product name>
              Component: <component (if applicable)>
                        
              Top Dislikes:
              - ...
              - ...
                        
            
                        
            """;
    }