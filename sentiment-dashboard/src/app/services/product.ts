import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProductService {

  private selectedProduct = new BehaviorSubject<number | null>(null);
  selectedProduct$ = this.selectedProduct.asObservable();

  private componentIdSource = new BehaviorSubject<number | null>(null);
  selectedComponent$ = this.componentIdSource.asObservable();

  setProductId(id: number){
    this.selectedProduct.next(id);
  }

  setComponentId(id: number){
    this.componentIdSource.next(id);
  }

}