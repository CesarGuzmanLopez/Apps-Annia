import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-header-nav',
  standalone: true,
  imports: [CommonModule],
  template: `
    <header class="app-header">
      <div class="header-content">
        <button class="btn-back" (click)="goBack()" title="Volver al menú">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M 19 12 H 5 M 5 12 L 12 19 M 5 12 L 12 5"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          <span>Menú</span>
        </button>

        <div class="header-title">
          <img *ngIf="logo" [src]="logo" [alt]="title" class="logo" />
          <div>
            <h1>{{ title }}</h1>
            <p *ngIf="subtitle" class="subtitle">{{ subtitle }}</p>
          </div>
        </div>

        <div class="spacer"></div>
      </div>
    </header>
  `,
  styles: [
    `
      .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        position: sticky;
        top: 0;
        z-index: 100;
      }

      .header-content {
        display: flex;
        align-items: center;
        gap: 20px;
        max-width: 1200px;
        margin: 0 auto;
      }

      .btn-back {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 16px;
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        font-size: 0.9rem;
        white-space: nowrap;

        svg {
          width: 18px;
          height: 18px;
        }

        &:hover {
          background: rgba(255, 255, 255, 0.3);
          border-color: rgba(255, 255, 255, 0.5);
          transform: translateX(-4px);
        }

        &:active {
          transform: scale(0.95);
        }
      }

      .header-title {
        display: flex;
        align-items: center;
        gap: 16px;
        flex: 1;

        .logo {
          width: 60px;
          height: 60px;
          object-fit: contain;
          filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2));
          border-radius: 8px;
          padding: 4px;
          background: rgba(255, 255, 255, 0.1);
        }

        h1 {
          margin: 0;
          font-size: 1.8rem;
          font-weight: 700;
          line-height: 1.2;
        }

        .subtitle {
          margin: 4px 0 0 0;
          font-size: 0.9rem;
          opacity: 0.9;
        }
      }

      .spacer {
        flex: 1;
      }

      @media (max-width: 768px) {
        .header-content {
          gap: 12px;
        }

        .btn-back {
          padding: 8px 12px;
          font-size: 0.85rem;

          svg {
            width: 16px;
            height: 16px;
          }
        }

        .header-title {
          gap: 12px;

          .logo {
            width: 50px;
            height: 50px;
          }

          h1 {
            font-size: 1.3rem;
          }
        }
      }

      @media (max-width: 480px) {
        .header-content {
          flex-direction: column;
          gap: 12px;
        }

        .btn-back span {
          display: none;
        }

        .header-title {
          gap: 10px;

          .logo {
            width: 45px;
            height: 45px;
          }

          h1 {
            font-size: 1.2rem;
          }

          .subtitle {
            display: none;
          }
        }

        .spacer {
          display: none;
        }
      }
    `,
  ],
})
export class AppHeaderComponent {
  @Input() title: string = '';
  @Input() subtitle?: string;
  @Input() logo?: string;

  constructor(private router: Router) {}

  goBack() {
    this.router.navigate(['/']);
  }
}
