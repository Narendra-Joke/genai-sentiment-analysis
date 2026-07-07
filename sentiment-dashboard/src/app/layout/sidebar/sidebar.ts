import { Component, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { ProductService } from '../../services/product';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css'
})
export class SidebarComponent {

  activeSubMenu: string = '';
  
  families: any[] = [];
  components: any[] = [];

  // ✅ Year filter
  currentYear = new Date().getFullYear();
  years: number[] = [];
  selectedYear: number = this.currentYear;

  constructor(
    private http: HttpClient, 
    private cd: ChangeDetectorRef, 
    private productService: ProductService
  ) {
    this.years = [
      this.currentYear,
      this.currentYear - 1,
      this.currentYear - 2
    ];
  }

  toggle(menu: string) {

    if (this.activeSubMenu === menu) {
      this.activeSubMenu = '';
      return;
    }

    this.activeSubMenu = menu;

    // ✅ PRODUCTS
    if (menu === 'products') {
      this.selectedYear = this.currentYear;
      this.loadProducts(this.selectedYear);
    }

    // ✅ COMPONENTS (unchanged)
    if (menu === 'components' && this.components.length === 0) {
      this.loadComponents();
    }
  }

  /* ---------------- PRODUCTS ---------------- */

  loadProducts(year?: number) {

    const y = year ?? this.selectedYear;

    this.http.get<any[]>(`http://localhost:8082/api/products/families?year=${y}`)
      .subscribe({
        next: (data) => {
          this.families = data;
          this.cd.detectChanges();
        },
        error: (err) => {
          console.error('Error loading products:', err);
        }
      });
  }

  selectYear(year: number){
    this.selectedYear = year;
    this.loadProducts(year);
  }

  selectProduct(id:number){
    this.productService.setProductId(id);
  }

  selectComponent(id:number){
    this.productService.setComponentId(id);
  }

  /* ---------------- COMPONENTS ---------------- */

  loadComponents(){
    this.http.get<any[]>('http://localhost:8082/api/components')
      .subscribe({
        next: (data) => {
          this.components = data;
          this.cd.detectChanges();
        },
        error: (err) => {
          console.error('Error loading components:', err);
        }
      });
  }

}