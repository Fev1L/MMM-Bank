import {Component, OnInit, inject, ChangeDetectorRef, ElementRef} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  Firestore,
  collection,
  query,
  onSnapshot,
  orderBy,
  addDoc,
  Timestamp,
  collectionGroup,
  collectionData
} from '@angular/fire/firestore';

@Component({
  selector: 'app-admin-support',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-support.html',
  styleUrls: ['./admin-support.scss']
})
export class AdminSupport implements OnInit {
  private cdr = inject(ChangeDetectorRef);

  chats: any[] = [];
  selectedChatId: string | null = null;
  messages: any[] = [];
  replyText: string = '';

  constructor(
    private firestore: Firestore
  ) {}

  ngOnInit() {
    this.loadAllChats();
  }

  loadAllChats() {
    const chatsRef = collection(this.firestore, 'chats');
    collectionData(chatsRef, { idField: 'id' }).subscribe((data: any[]) => {
      this.chats = data;
      this.cdr.detectChanges();
    });
  }

  selectChat(chatId: string) {
    this.selectedChatId = chatId;
    const msgRef = collection(this.firestore, `chats/${chatId}/messages`);
    const q = query(msgRef, orderBy('time', 'asc'));

    collectionData(q, { idField: 'id' }).subscribe((messages: any[]) => {
      this.messages = messages.map(msg => ({
        ...msg,
        time: msg.time?.toDate?.()
      }));
      this.cdr.detectChanges();
    });
  }

  async sendReply() {
    if (!this.replyText.trim() || !this.selectedChatId) return;

    const messageData = {
      sender: 'admin',
      text: this.replyText,
      time: Timestamp.now()
    };

    try {
      await addDoc(collection(this.firestore, `chats/${this.selectedChatId}/messages`), messageData);
      this.replyText = '';
      this.cdr.detectChanges();
    } catch (err) {
      console.error('Error sending reply:', err);
    }
  }
}
