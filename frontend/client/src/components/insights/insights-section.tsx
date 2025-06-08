import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, DollarSign, CreditCard, Users, AlertCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import type { WeeklyInsights } from "@shared/schema";

interface InsightCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  format?: 'currency' | 'percentage' | 'number';
}

function InsightCard({ title, value, change, icon, format = 'number' }: InsightCardProps) {
  const formatValue = (val: string | number) => {
    if (format === 'currency') {
      return `₹${typeof val === 'number' ? val.toLocaleString() : val}`;
    }
    if (format === 'percentage') {
      return `${val}%`;
    }
    return typeof val === 'number' ? val.toLocaleString() : val;
  };

  const isPositive = change && change > 0;
  const isNegative = change && change < 0;

  return (
    <Card className="bg-white border border-gray-200 hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">{title}</CardTitle>
        <div className="text-pine-blue">{icon}</div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-gray-900">{formatValue(value)}</div>
        {change !== undefined && (
          <div className="flex items-center mt-1">
            {isPositive && <TrendingUp className="w-3 h-3 text-green-500 mr-1" />}
            {isNegative && <TrendingDown className="w-3 h-3 text-red-500 mr-1" />}
            <span className={`text-xs ${isPositive ? 'text-green-600' : isNegative ? 'text-red-600' : 'text-gray-500'}`}>
              {change > 0 ? '+' : ''}{change}% from last week
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function InsightsSection() {
  const { data: insights, isLoading } = useQuery<WeeklyInsights>({
    queryKey: ["/api/insights/weekly"],
    enabled: true,
  });

  if (isLoading) {
    return (
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Last Week Insights</h2>
          <p className="text-sm text-gray-500">Loading performance data...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="bg-white border border-gray-200">
              <CardHeader className="pb-2">
                <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded animate-pulse mb-2"></div>
                <div className="h-3 bg-gray-200 rounded animate-pulse w-24"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!insights) {
    return (
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Last Week Insights</h2>
            <p className="text-sm text-gray-500">Connect your Pine Labs account to view insights</p>
          </div>
          <Badge variant="outline" className="text-gray-500 border-gray-300">
            No Data
          </Badge>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-6 text-center">
          <AlertCircle className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-600 text-sm">
            Please connect your Pine Labs merchant account to view transaction insights and analytics.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border-b border-gray-200 p-4">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Last Week Insights</h2>
          <p className="text-sm text-gray-500">Performance overview for your Pine Labs account</p>
        </div>
        <Badge variant="outline" className="text-pine-blue border-pine-blue">
          Live Data
        </Badge>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <InsightCard
          title="Total Transactions"
          value={insights?.totalTransactions ?? 0}
          change={insights?.transactionChange}
          icon={<CreditCard className="w-4 h-4" />}
        />
        
        <InsightCard
          title="Total Revenue"
          value={insights?.totalRevenue ?? 0}
          change={insights?.revenueChange}
          icon={<DollarSign className="w-4 h-4" />}
          format="currency"
        />
        
        <InsightCard
          title="Active Customers"
          value={insights?.activeCustomers ?? 0}
          change={insights?.customerChange}
          icon={<Users className="w-4 h-4" />}
        />
        
        <InsightCard
          title="Failure Rate"
          value={insights?.failureRate ?? 0}
          change={insights?.failureChange}
          icon={<AlertCircle className="w-4 h-4" />}
          format="percentage"
        />
      </div>
      
      {insights?.topPaymentMethod && insights?.averageTicket && (
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-pine-light dark:bg-pine-light rounded-lg p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-pine-dark dark:text-pine-dark font-medium">Top Payment Method</span>
              <Badge className="bg-pine-blue text-white">{insights.topPaymentMethod}</Badge>
            </div>
          </div>
          
          <div className="bg-pine-light dark:bg-pine-light rounded-lg p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-pine-dark dark:text-pine-dark font-medium">Average Ticket Size</span>
              <span className="text-sm font-semibold text-pine-dark dark:text-pine-dark">₹{insights.averageTicket.toLocaleString()}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}