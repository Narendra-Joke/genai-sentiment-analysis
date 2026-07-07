import { Component, ViewChild, ElementRef, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chatbot.html',
  styleUrl: './chatbot.css'
})
export class ChatbotComponent {

  isOpen = false;
  question = '';
  messages: any[] = [];

  @ViewChild('chatBody') chatBody!: ElementRef;

  constructor(
    private http: HttpClient,
    private cdr: ChangeDetectorRef
  ) {}

  toggleChat() {
    this.isOpen = !this.isOpen;
  }

  sendMessage() {

    if (!this.question.trim()) return;

    const userMessage = this.question;

    // 1. Add user message
    this.messages.push({
      type: 'user',
      text: userMessage
    });

    this.question = '';
    this.updateUI();

    // 2. Add typing indicator
    const typingIndex = this.messages.push({
      type: 'bot',
      text: 'Typing...'
    }) - 1;

    this.updateUI();

    // 3. API call
    this.http.post<any>('http://localhost:8082/api/chat', {
      question: userMessage
    })
    .subscribe({

      next: (res) => {

        // ✅ Replace object (NOT mutate)
        this.messages[typingIndex] = {
          type: 'bot',
          text: res.answer
        };

        this.updateUI();
      },

      error: () => {

        this.messages[typingIndex] = {
          type: 'bot',
          text: 'Sorry, something went wrong while fetching the response.'
        };

        this.updateUI();
      }

    });
  }

  // 🔥 Central UI updater
  updateUI() {
    this.messages = [...this.messages]; // force change detection
    this.cdr.detectChanges();          // extra safety
    this.scrollToBottom();
  }

  scrollToBottom() {
    setTimeout(() => {
      if (this.chatBody) {
        this.chatBody.nativeElement.scrollTop =
          this.chatBody.nativeElement.scrollHeight;
      }
    }, 0);
  }

}