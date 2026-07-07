import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OauthSuccessComponent } from './oauth-success';

describe('OauthSuccess', () => {
  let component: OauthSuccessComponent;
  let fixture: ComponentFixture<OauthSuccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OauthSuccessComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OauthSuccessComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
