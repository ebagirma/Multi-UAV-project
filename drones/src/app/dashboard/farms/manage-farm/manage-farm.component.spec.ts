import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ManageFarmComponent } from './manage-farm.component';

describe('ManageFarmComponent', () => {
  let component: ManageFarmComponent;
  let fixture: ComponentFixture<ManageFarmComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ManageFarmComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ManageFarmComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
