# Smart-Accounting Software

An AI-powered, automated accounting platform designed to seamlessly bridge the gap between digital invoicing systems (like the Italian SDI) and traditional double-entry bookkeeping (*partita doppia*).

The software automatically parses incoming/outgoing XML invoices, maps them to a dynamic Chart of Accounts (*Piano dei Conti*), and generates accurate journal entries (`Debit` / `Credit`) with minimal human intervention.

---

## 🚀 Key Features

* **Automated SDI Integration:** Real-time fetching and parsing of electronic invoices (`.xml` format).
* **Smart Chart of Accounts Mapping:** AI-driven categorization of costs and revenues into their respective ledger accounts.
* **Automated Double-Entry Ledger:** Instant creation of journal entries with balanced Debits ($Dr.$) and Credits ($Cr.$).
* **Payment Reconciliation:** One-click matching of open vendor debts (*Fornitori*) and customer credits (*Clienti*) with bank statements.

---

## 🛠️ Tech Stack

* **Backend:** Python (FastAPI), Java Spring Boot*
* **Frontend:** Angular 
* **Database:** PostgreSQL

