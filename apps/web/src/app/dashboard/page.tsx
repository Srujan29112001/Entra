"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { supabase } from "@/lib/supabase";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  Calendar,
  MessageSquare,
  LogOut,
} from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface DashboardData {
  company: any;
  financials: any;
  runwayMonths: number;
  burnRate: number;
  metrics: {
    cashBalance: number;
    monthlyRevenue: number;
    monthlyExpenses: number;
    ltvCacRatio: number;
  };
}

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) {
        router.push("/auth/login");
        return;
      }

      // Get company
      const { data: companies } = await supabase
        .from("companies")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false })
        .limit(1);

      if (!companies || companies.length === 0) {
        router.push("/onboarding");
        return;
      }

      const company = companies[0];

      // Get latest financial snapshot
      const { data: financials } = await supabase
        .from("financial_snapshots")
        .select("*")
        .eq("company_id", company.id)
        .order("snapshot_date", { ascending: false })
        .limit(1)
        .single();

      setData({
        company,
        financials: financials || {},
        runwayMonths: financials?.runway_months || 0,
        burnRate: financials?.burn_rate || 0,
        metrics: {
          cashBalance: financials?.cash_balance || 0,
          monthlyRevenue: financials?.monthly_revenue || 0,
          monthlyExpenses: financials?.monthly_expenses || 0,
          ltvCacRatio: financials?.ltv && financials?.cac ? financials.ltv / financials.cac : 0,
        },
      });
    } catch (error) {
      console.error("Error loading dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push("/");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">No data available</div>
      </div>
    );
  }

  // Sample data for charts
  const revenueData = [
    { month: "Jan", revenue: data.metrics.monthlyRevenue * 0.6, expenses: data.metrics.monthlyExpenses * 0.7 },
    { month: "Feb", revenue: data.metrics.monthlyRevenue * 0.7, expenses: data.metrics.monthlyExpenses * 0.75 },
    { month: "Mar", revenue: data.metrics.monthlyRevenue * 0.8, expenses: data.metrics.monthlyExpenses * 0.85 },
    { month: "Apr", revenue: data.metrics.monthlyRevenue * 0.9, expenses: data.metrics.monthlyExpenses * 0.9 },
    { month: "May", revenue: data.metrics.monthlyRevenue * 0.95, expenses: data.metrics.monthlyExpenses * 0.95 },
    { month: "Jun", revenue: data.metrics.monthlyRevenue, expenses: data.metrics.monthlyExpenses },
  ];

  const expenseBreakdown = [
    { name: "Salaries", value: data.metrics.monthlyExpenses * 0.6 },
    { name: "Marketing", value: data.metrics.monthlyExpenses * 0.2 },
    { name: "Infrastructure", value: data.metrics.monthlyExpenses * 0.15 },
    { name: "Other", value: data.metrics.monthlyExpenses * 0.05 },
  ];

  const COLORS = ["#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b"];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">{data.company.name}</h1>
            <p className="text-sm text-muted-foreground">
              {data.company.industry} • {data.company.stage}
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => router.push("/chat")}>
              <MessageSquare className="h-4 w-4 mr-2" />
              Ask AI Advisors
            </Button>
            <Button variant="ghost" onClick={handleSignOut}>
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Cash Balance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="text-2xl font-bold">
                  {formatCurrency(data.metrics.cashBalance)}
                </div>
                <DollarSign className="h-5 w-5 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Monthly Revenue
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="text-2xl font-bold">
                  {formatCurrency(data.metrics.monthlyRevenue)}
                </div>
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Burn Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="text-2xl font-bold">{formatCurrency(Math.abs(data.burnRate))}</div>
                <TrendingDown className="h-5 w-5 text-red-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Runway
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="text-2xl font-bold">
                  {data.runwayMonths.toFixed(1)} months
                </div>
                <Calendar className="h-5 w-5 text-blue-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue vs Expenses */}
          <Card>
            <CardHeader>
              <CardTitle>Revenue & Expenses Trend</CardTitle>
              <CardDescription>Last 6 months</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} />
                  <Line type="monotone" dataKey="expenses" stroke="#ef4444" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Expense Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Expense Breakdown</CardTitle>
              <CardDescription>Current month distribution</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={expenseBreakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {expenseBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* AI Insights */}
        <Card>
          <CardHeader>
            <CardTitle>AI-Powered Insights</CardTitle>
            <CardDescription>Recommendations from your AI advisors</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {data.runwayMonths < 6 && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="font-semibold text-red-900">⚠️ Critical: Low Runway</p>
                <p className="text-sm text-red-700 mt-1">
                  With {data.runwayMonths.toFixed(1)} months of runway remaining, consider reducing burn rate or raising funds immediately.
                </p>
              </div>
            )}

            {data.metrics.ltvCacRatio > 0 && data.metrics.ltvCacRatio < 3 && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="font-semibold text-yellow-900">⚡ LTV:CAC Ratio Needs Improvement</p>
                <p className="text-sm text-yellow-700 mt-1">
                  Your LTV:CAC ratio is {data.metrics.ltvCacRatio.toFixed(2)}. Aim for 3:1 or higher for sustainable growth.
                </p>
              </div>
            )}

            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="font-semibold text-blue-900">💡 Ask Your AI Board</p>
              <p className="text-sm text-blue-700 mt-1 mb-3">
                Get personalized advice on finance, tax, strategy, legal, and wealth management.
              </p>
              <Button onClick={() => router.push("/chat")}>
                <MessageSquare className="h-4 w-4 mr-2" />
                Start Conversation
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
