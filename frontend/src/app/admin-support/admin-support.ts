import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Firestore, collection, query, onSnapshot, orderBy, addDoc, Timestamp, collectionGroup } from '@angular/fire/firestore';

@Component({
  selector: 'app-admin-support',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-support.html',
  styleUrls: ['./admin-support.scss']
})
export class AdminSupport implements OnInit {
  private firestore = inject(Firestore);
  private cdr = inject(ChangeDetectorRef);

  chats: any[] = [];
  selectedChatId: string | null = null;
  messages: any[] = [];
  replyText: string = '';

  ngOnInit() {
    this.loadAllChats();
  }

  loadAllChats() {
    const chatsRef = collection(this.firestore, 'chats');
    onSnapshot(chatsRef, (snapshot) => {
      this.chats = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      this.cdr.detectChanges();
    });
  }

  selectChat(chatId: string) {
    this.selectedChatId = chatId;
    const msgRef = collection(this.firestore, `chats/${chatId}/messages`);
    const q = query(msgRef, orderBy('time', 'asc'));

    onSnapshot(q, (snapshot) => {
      this.messages = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        time: (doc.data() as any).time?.toDate()
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
