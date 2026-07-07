import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header.html',
  styleUrl: './header.css'
})
export class HeaderComponent implements OnInit {

  showMenu = false;

  picture = '';
  email = '';
  initial = '';

  constructor(private auth: AuthService) {}

  ngOnInit(): void {

    const token = localStorage.getItem('token');

    if (!token) return;

    const payload = JSON.parse(atob(token.split('.')[1]));

    this.email = payload.sub;
    this.picture = payload.picture;

    const name = payload.name || payload.sub;

    this.initial = name.charAt(0).toUpperCase();

  }

  toggleMenu() {
    this.showMenu = !this.showMenu;
  }

  logout() {
    this.auth.logout();
  }

}