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
  collectionData,
  doc,
  setDoc,
} from '@angular/fire/firestore';

@Component({
  selector: 'app-admin-support',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-support.html',
  styleUrls: ['./admin-support.scss'],
})
export class AdminSupport implements OnInit {
  private cdr = inject(ChangeDetectorRef);

  chats: any[] = [];
  selectedChatId: string | null = null;
  messages: any[] = [];
  replyText: string = '';

  isSendingReply = false;

  constructor(private firestore: Firestore) {}

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
      this.messages = messages.map((msg) => ({
        ...msg,
        time: msg.time?.toDate?.(),
      }));
      this.cdr.detectChanges();
    });
  }

  async sendReply() {
    if (!this.replyText.trim() || !this.selectedChatId || this.isSendingReply) return;

    this.isSendingReply = true;

    const deleteTime = new Date();
    deleteTime.setHours(deleteTime.getHours() + 1);

    const chatDocRef = doc(this.firestore, `chats/${this.selectedChatId}`);
    const messagesColRef = collection(this.firestore, `chats/${this.selectedChatId}/messages`);

    try {
      await Promise.all([
        addDoc(messagesColRef, {
          sender: 'admin',
          text: this.replyText,
          time: Timestamp.now(),
        }),
        setDoc(
          chatDocRef,
          {
            expireAt: Timestamp.fromDate(deleteTime),
            lastUpdate: Timestamp.now(),
            status: 'answered',
          },
          { merge: true },
        ),
      ]);

      this.replyText = '';
    } catch (err) {
      console.error('Error sending reply:', err);
    } finally {
      this.isSendingReply = false;
      this.cdr.detectChanges();
    }
  }
}
