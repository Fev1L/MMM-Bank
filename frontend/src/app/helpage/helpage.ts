import {
  Component,
  OnInit,
  ChangeDetectorRef,
  ElementRef,
  HostListener,
  ViewChild,
  inject,
  PLATFORM_ID
} from '@angular/core';
import { Router } from '@angular/router';
import {CommonModule, isPlatformBrowser} from '@angular/common';
import { AuthService } from '../core/services/auth';
import { AlertService } from '../core/services/alert';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import {
  Firestore,
  collection,
  addDoc,
  query,
  orderBy,
  Timestamp,
  setDoc,
  doc, collectionData
} from '@angular/fire/firestore';

@Component({
  selector: 'app-helpage',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './helpage.html',
  styleUrl: './helpage.scss',
})
export class Helpage implements OnInit {
  user: any = null;
  isUserLoggedIn: boolean = false;
  isSending = false;

  allQuestions: any[] = [];
  filteredResults: any[] = [];
  searchTerm: string = '';

  selectedArticle: any = null;
  isModalOpen: boolean = false;

  isResultsVisible: boolean = false;
  @ViewChild('searchContainer') searchContainer!: ElementRef;

  isChatOpen: boolean = false;
  chatMessages: any[] = [];
  newMessage: string = '';
  chatId: string = '';
  @ViewChild('scrollMe') private myScrollContainer!: ElementRef;
  @ViewChild('searchInput') searchInput!: ElementRef;
  private platformId = inject(PLATFORM_ID);

  constructor(
    private router: Router,
    private authService: AuthService,
    private alertService: AlertService,
    private cdr: ChangeDetectorRef,
    private eRef: ElementRef,
    private http: HttpClient,
    private firestore: Firestore,
  ) {}

  ngOnInit() {
    this.loadFaqData();

    if (isPlatformBrowser(this.platformId)) {
      this.initAuthAndChat();
    }
  }

  goBack() {
    if (this.isUserLoggedIn) {
      this.router.navigate(['/dashboard']);
    } else {
      this.router.navigate(['/']);
    }
  }

  loadFaqData() {
    this.http.get<any[]>('/faq.json').subscribe({
      next: (data) => {
        this.allQuestions = data;
      },
      error: (err) => console.error('Could not load FAQ data', err),
    });
  }

  openArticle(article: any) {
    this.selectedArticle = article;
    this.isModalOpen = true;
    this.isResultsVisible = false;
    document.body.style.overflow = 'hidden';
  }

  closeArticle() {
    this.isModalOpen = false;
    setTimeout(() => {
      this.selectedArticle = null;
      document.body.style.overflow = 'auto';
    }, 300);
  }

  rateArticle() {
    this.closeArticle();
    this.alertService.success(`Thank you for your feedback!`);
  }

  @HostListener('document:click', ['$event'])
  clickout(event: any) {
    if (this.searchContainer && !this.searchContainer.nativeElement.contains(event.target)) {
      this.closeResults();
    }
  }

  onSearch(event?: any) {
    const rawValue = event ? event.target.value : this.searchTerm;

    const query = this.searchTerm.toLowerCase().trim();

    if (query.length > 1) {
      this.filteredResults = this.allQuestions
        .filter((item) => {
          const titleMatch = item.title?.toLowerCase().includes(query);
          const tagsMatch = item.tags?.toLowerCase().includes(query);
          const categoryMatch = item.category?.toLowerCase().includes(query);

          return titleMatch || tagsMatch || categoryMatch;
        })
        .slice(0, 6);

      this.isResultsVisible = this.filteredResults.length > 0;
    } else {
      this.isResultsVisible = false;
    }

    this.cdr.detectChanges();
  }

  closeResults() {
    if (this.isResultsVisible) {
      this.isResultsVisible = false;
      this.cdr.detectChanges();
    }
  }

  openChatModal() {
    this.isChatOpen = true;
    document.body.style.overflow = 'hidden';
    this.cdr.detectChanges();
  }

  closeChatModal() {
    this.isChatOpen = false;
    document.body.style.overflow = 'auto';
    this.cdr.detectChanges();
  }

  async sendMessage() {
    if (this.isSending || !this.newMessage.trim()) return;

    this.isSending = true;
    const deleteTime = new Date();
    deleteTime.setHours(deleteTime.getHours() + 1);

    const chatDocRef = doc(this.firestore, `chats/${this.chatId}`);
    const messagesColRef = collection(this.firestore, `chats/${this.chatId}/messages`);

    try {
      await Promise.all([
        setDoc(
          chatDocRef,
          {
            lastUpdate: Timestamp.now(),
            expireAt: Timestamp.fromDate(deleteTime),
            userId: this.chatId,
            status: 'active',
          },
          { merge: true },
        ),
        addDoc(messagesColRef, {
          sender: 'user',
          text: this.newMessage,
          time: Timestamp.now(),
        }),
      ]);

      this.newMessage = '';
    } catch (e) {
      console.error('Error:', e);
    } finally {
      this.isSending = false;
      this.cdr.detectChanges();
    }
  }

  listenToMessages() {
    const msgCollection = collection(this.firestore, `chats/${this.chatId}/messages`);
    const q = query(msgCollection, orderBy('time', 'asc'));

    collectionData(q, { idField: 'id' }).subscribe((messages: any[]) => {
      this.chatMessages = messages.map((msg) => ({
        ...msg,
        time: msg.time?.toDate?.(),
      }));
    });
  }

  scrollToBottom(): void {
    try {
      setTimeout(() => {
        this.myScrollContainer.nativeElement.scrollTop =
          this.myScrollContainer.nativeElement.scrollHeight;
      }, 100);
    } catch (err) {}
  }

  filterByCategory(category: string) {
    this.searchTerm = category;
    this.onSearch();

    setTimeout(() => {
      this.searchInput.nativeElement.focus();
    }, 100);

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  openTrending(title: string) {
    const article = this.allQuestions.find((q) => q.title.toLowerCase() === title.toLowerCase());

    if (article) {
      this.openArticle(article);
    } else {
      this.searchTerm = title;
      this.onSearch({ target: { value: title } });
    }
  }

  loadUserData() {
    this.authService.getUserData().subscribe({
      next: (res: any) => {
        this.user = res.user;
        this.isUserLoggedIn = true;
        this.chatId = `user_${this.user?.id}`;
        this.listenToMessages();
        this.cdr.detectChanges();
      },
      error: () => {
        this.isUserLoggedIn = false;
        this.initGuestChat();
      },
    });
  }

  private initAuthAndChat() {
    const token = localStorage.getItem('token');
    this.isUserLoggedIn = !!token;

    if (this.isUserLoggedIn) {
      this.loadUserData();
    } else {
      this.initGuestChat();
    }
  }

  private initGuestChat() {
    if (!isPlatformBrowser(this.platformId)) return;

    let guestId = localStorage.getItem('guest_chat_id');

    if (!guestId) {
      guestId = 'guest_' + Math.random().toString(36).substring(2, 11);
      localStorage.setItem('guest_chat_id', guestId);
    }

    this.chatId = guestId;
    this.listenToMessages();
  }
}
