export const pinelabsKnowledgeBase = {
  transactions: {
    viewHistory: "Access your transaction history through the Pine Labs merchant dashboard. Navigate to 'Transactions' section to view all payment records.",
    searchTransactions: "Use filters in the transaction dashboard to search by date, amount, payment method, or status.",
    downloadReports: "Export transaction reports in CSV or PDF format from the dashboard for your records."
  },
  
  settlements: {
    timings: "Settlement timings vary by payment method: Credit Cards (2-3 business days), Debit Cards (1-2 business days), UPI (same day to next business day).",
    tracking: "Track settlement status in the 'Settlements' section of your merchant dashboard.",
    delays: "Settlement delays may occur due to bank holidays, technical issues, or compliance checks."
  },
  
  commissions: {
    creditCards: "Credit card transaction fees typically range from 1.8% to 2.5% depending on merchant category and volume.",
    debitCards: "Debit card transaction fees range from 0.9% to 1.2%.",
    upi: "UPI transaction fees range from 0% to 0.5%, often with promotional rates for new merchants.",
    factors: "Rates depend on merchant category, monthly volume, and business type."
  },
  
  refunds: {
    process: "Initiate refunds through the transaction history by selecting the transaction and clicking 'Refund'.",
    timeline: "Refunds are typically processed within 5-7 business days to the customer's account.",
    partialRefunds: "Partial refunds are supported - enter the specific amount to be refunded.",
    restrictions: "Refunds can only be processed within 180 days of the original transaction."
  },
  
  support: {
    phone: "24/7 support available at 1800-XXX-XXXX",
    email: "Email support at support@pinelabs.com",
    dashboard: "Access self-service options through your merchant dashboard",
    emergencyContact: "For urgent issues, use the emergency support line in your merchant app"
  },
  
  technicalIssues: {
    paymentFailures: "Check network connectivity, verify card details, and ensure sufficient balance. Contact support if issues persist.",
    terminalIssues: "Restart the terminal, check connections, and verify network status. Contact technical support for hardware issues.",
    dashboardAccess: "Clear browser cache, try incognito mode, or contact support for login issues."
  },

  getRelevantInfo(query: string): string {
    const lowerQuery = query.toLowerCase();
    let relevantInfo: string[] = [];

    if (lowerQuery.includes('transaction') || lowerQuery.includes('history') || lowerQuery.includes('payment')) {
      relevantInfo.push(
        `Transaction Management: ${this.transactions.viewHistory}`,
        `Search Transactions: ${this.transactions.searchTransactions}`,
        `Download Reports: ${this.transactions.downloadReports}`
      );
    }

    if (lowerQuery.includes('settlement') || lowerQuery.includes('money') || lowerQuery.includes('timing')) {
      relevantInfo.push(
        `Settlement Timings: ${this.settlements.timings}`,
        `Settlement Tracking: ${this.settlements.tracking}`,
        `Settlement Delays: ${this.settlements.delays}`
      );
    }

    if (lowerQuery.includes('commission') || lowerQuery.includes('fee') || lowerQuery.includes('rate') || lowerQuery.includes('charge')) {
      relevantInfo.push(
        `Credit Card Fees: ${this.commissions.creditCards}`,
        `Debit Card Fees: ${this.commissions.debitCards}`,
        `UPI Fees: ${this.commissions.upi}`,
        `Rate Factors: ${this.commissions.factors}`
      );
    }

    if (lowerQuery.includes('refund') || lowerQuery.includes('return') || lowerQuery.includes('cancel')) {
      relevantInfo.push(
        `Refund Process: ${this.refunds.process}`,
        `Refund Timeline: ${this.refunds.timeline}`,
        `Partial Refunds: ${this.refunds.partialRefunds}`,
        `Refund Restrictions: ${this.refunds.restrictions}`
      );
    }

    if (lowerQuery.includes('support') || lowerQuery.includes('help') || lowerQuery.includes('contact') || lowerQuery.includes('problem')) {
      relevantInfo.push(
        `Phone Support: ${this.support.phone}`,
        `Email Support: ${this.support.email}`,
        `Dashboard Help: ${this.support.dashboard}`,
        `Emergency Contact: ${this.support.emergencyContact}`
      );
    }

    if (lowerQuery.includes('fail') || lowerQuery.includes('error') || lowerQuery.includes('issue') || lowerQuery.includes('problem')) {
      relevantInfo.push(
        `Payment Failures: ${this.technicalIssues.paymentFailures}`,
        `Terminal Issues: ${this.technicalIssues.terminalIssues}`,
        `Dashboard Access: ${this.technicalIssues.dashboardAccess}`
      );
    }

    // If no specific category matches, return general information
    if (relevantInfo.length === 0) {
      relevantInfo = [
        `General Support: ${this.support.phone}`,
        `Settlement Info: ${this.settlements.timings}`,
        `Transaction Access: ${this.transactions.viewHistory}`
      ];
    }

    return relevantInfo.join('\n');
  }
};
