/**
 * TypeScript types matching the API Pydantic models.
 */

export interface Expense {
  date: string;
  amount: number;
}

export interface Transaction {
  date: string;
  amount: number;
  ceiling: number;
  remanent: number;
}

export interface InvalidTransaction {
  date: string;
  amount: number;
  ceiling?: number;
  remanent?: number;
  message: string;
}

export interface ValidFilteredTransaction extends Transaction {
  inKPeriod: boolean;
}

export interface QPeriod {
  fixed: number;
  start: string;
  end: string;
}

export interface PPeriod {
  extra: number;
  start: string;
  end: string;
}

export interface KPeriod {
  start: string;
  end: string;
}

export interface ValidatorRequest {
  wage: number;
  transactions: Transaction[];
}

export interface ValidatorResponse {
  valid: Transaction[];
  invalid: InvalidTransaction[];
}

export interface FilterRequest {
  q: QPeriod[];
  p: PPeriod[];
  k: KPeriod[];
  wage: number;
  transactions: Expense[];
}

export interface FilterResponse {
  valid: ValidFilteredTransaction[];
  invalid: InvalidTransaction[];
}

export interface ReturnsRequest {
  age: number;
  wage: number;
  inflation: number;
  q: QPeriod[];
  p: PPeriod[];
  k: KPeriod[];
  transactions: Expense[];
}

export interface SavingsByDate {
  start: string;
  end: string;
  amount: number;
  profit: number;
  taxBenefit: number;
}

export interface ReturnsResponse {
  totalTransactionAmount: number;
  totalCeiling: number;
  savingsByDates: SavingsByDate[];
}

export interface PerformanceResponse {
  time: string;
  memory: string;
  threads: number;
}
