import {Component, AfterViewInit, ElementRef, ViewChild} from '@angular/core';
import {RouterLink} from '@angular/router';
import {NgForOf, NgIf} from '@angular/common';

@Component({
  selector: 'app-home',
  imports: [
    RouterLink,
    NgIf,
    NgForOf
  ],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})

export class Home implements AfterViewInit {
  @ViewChild('scrollContainer') scrollContainer!: ElementRef;

  activeTab: 'personal' | 'business' | 'about' = 'personal';
  activeReport: number = 0;
  reports = [
    { title: 'The Beginning', icon: '🐣', items: ['Naive start', 'DB setup', 'Coffee fuel'] },
    { title: 'Mechanics', icon: '⚙️', items: ['User Auth', 'Transfers', 'Balances'] },
    { title: 'Financials', icon: '📈', items: ['Credits', 'Deposits', 'History'] },
    { title: 'Social & Fun', icon: '🃏', items: ['Casino mod', 'Friends', 'Inbox'] },
    { title: 'TOP SECRET', icon: '🤐', items: ['UI Overhaul', 'Angular', 'Piggy Banks'] },
    { title: 'Final', icon: '👑', items: ['Final Release', 'Success', 'Best banking'] }
  ];

  constructor(private el: ElementRef) {}

  setActiveTab(tab: 'personal' | 'business' | 'about') {
    this.activeTab = tab;

    window.scrollTo({ top: 0, behavior: 'instant' });

    setTimeout(() => {
      this.initScrollAnimations();
      if (tab === 'about') {
        this.scrollToReport(this.activeReport, true);
      }
    }, 50);
  }

  ngAfterViewInit() {
    this.initScrollAnimations();
  }

  private initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
        }
      });
    }, { threshold: 0.1 });

    const revealElements = this.el.nativeElement.querySelectorAll('.reveal');
    revealElements.forEach((el: Element) => observer.observe(el));
  }

  selectReport(index: number) {
    this.activeReport = index;
    this.scrollToReport(index);
  }

  scrollToReport(index: number, instant: boolean = false) {
    const container = this.scrollContainer?.nativeElement;
    if (!container) return;

    const elements = container.querySelectorAll('.mono-step');
    const target = elements[index] as HTMLElement;

    if (target) {
      const containerRect = container.getBoundingClientRect();
      const targetRect = target.getBoundingClientRect();

      const scrollLeft = (targetRect.left - containerRect.left) + container.scrollLeft - (containerRect.width / 2) + (targetRect.width / 2);

      container.scrollTo({
        left: scrollLeft,
        behavior: instant ? 'auto' : 'smooth'
      });
    }
  }

  getProgressWidth(): string {
    return (this.activeReport / (this.reports.length - 1)) * 100 + '%';
  }
}
