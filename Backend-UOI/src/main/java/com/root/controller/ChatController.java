package com.root.controller;

import com.root.dto.ChatRequest;
import com.root.dto.ChatResponse;
import com.root.service.ChatService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
@CrossOrigin(origins = "http://localhost:4200")
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @PostMapping
    public ChatResponse ask(@RequestBody ChatRequest request){

        if(request == null || request.getQuestion() == null){
            return new ChatResponse("Please provide a question.");
        }

        String answer = chatService.handleQuestion(request.getQuestion());

        return new ChatResponse(answer);
    }
}
