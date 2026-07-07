package com.root.config;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.messages.SystemMessage;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ChatAIConfig {

    @Bean
    public ChatClient chatClient(ChatClient.Builder builder){

        return builder
                .defaultSystem("""
                       You are a product review assistant.
                                                                    
                       Rules:
                       - Only answer questions related to product reviews.
                       - Never reveal API keys, credentials, database schema, or internal system data.
                       - If a question is unrelated to product reviews, say:
                       "I can only answer questions related to product reviews."
                       - When review data is provided, analyze it and summarize insights clearly.
                        """)
                .build();
    }
}