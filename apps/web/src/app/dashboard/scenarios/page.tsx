"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { supabase } from "@/lib/supabase";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { ArrowLeft, Plus, TrendingUp, TrendingDown, DollarSign, Users, Calendar } from "lucide-react";

interface Scenario {
  id: string;
  name: string;
  description: string;
  growth_rate: number;
  funding_amount: number;
  months_to_simulate: number;
  projections: any;
  created_at: string;
}

export default function ScenariosPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [companyId, setCompanyId] = useState<string | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Form state for new scenario
  const [scenarioName, setScenarioName] = useState("");
  const [scenarioDescription, setScenarioDescription] = useState("");
  const [growthRate, setGrowthRate] = useState("10");
  const [fundingAmount, setFundingAmount] = useState("0");
  const [monthsToSimulate, setMonthsToSimulate] = useState("12");
  const [priceIncrease, setPriceIncrease] = useState("0");
  const [newHires, setNewHires] = useState("0");

  useEffect(() => {
    loadCompanyAndScenarios();
  }, []);

  const loadCompanyAndScenarios = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();

      if (!user) {
        router.push("/auth/login");
        return;
      }

      // Get company
      const { data: companies } = await supabase
        .from("companies")
        .select("id")
        .eq("user_id", user.id)
        .limit(1);

      if (!companies || companies.length === 0) {
        router.push("/onboarding");
        return;
      }

      const compId = companies[0].id;
      setCompanyId(compId);

      // Load scenarios
      const { data: scenarioData } = await supabase
        .from("scenarios")
        .select("*")
        .eq("company_id", compId)
        .order("created_at", { ascending: false });

      setScenarios(scenarioData || []);
    } catch (error) {
      console.error("Error loading data:", error);
    } finally {
      setLoading(false);
    }
  };

  const createScenario = async () => {
    if (!companyId || !scenarioName) return;

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // Get current financial snapshot
      const { data: snapshot } = await supabase
        .from("financial_snapshots")
        .select("*")
        .eq("company_id", companyId)
        .order("snapshot_date", { ascending: false })
        .limit(1)
        .single();

      if (!snapshot) {
        alert("Please set up your financial data first");
        return;
      }

      // Generate projections
      const projections = generateProjections(
        snapshot,
        parseFloat(growthRate) / 100,
        parseFloat(fundingAmount),
        parseInt(monthsToSimulate),
        parseFloat(priceIncrease) / 100,
        parseInt(newHires)
      );

      // Save scenario
      const { data: newScenario, error } = await supabase
        .from("scenarios")
        .insert({
          company_id: companyId,
          user_id: user.id,
          name: scenarioName,
          description: scenarioDescription,
          growth_rate: parseFloat(growthRate) / 100,
          funding_amount: parseFloat(fundingAmount),
          months_to_simulate: parseInt(monthsToSimulate),
          price_changes: { increase: parseFloat(priceIncrease) },
          hiring_plan: { new_hires: parseInt(newHires) },
          projections: projections,
          summary: {
            final_cash: projections[projections.length - 1].cash,
            final_revenue: projections[projections.length - 1].revenue,
            total_expenses: projections.reduce((sum: number, p: any) => sum + p.expenses, 0),
          },
        })
        .select()
        .single();

      if (error) throw error;

      // Refresh scenarios
      await loadCompanyAndScenarios();
      setDialogOpen(false);

      // Reset form
      setScenarioName("");
      setScenarioDescription("");
      setGrowthRate("10");
      setFundingAmount("0");
      setMonthsToSimulate("12");
      setPriceIncrease("0");
      setNewHires("0");
    } catch (error) {
      console.error("Error creating scenario:", error);
      alert("Failed to create scenario");
    }
  };

  const generateProjections = (
    currentSnapshot: any,
    monthlyGrowthRate: number,
    additionalFunding: number,
    months: number,
    priceIncreaseRate: number,
    additionalHires: number
  ) => {
    const projections = [];
    let cash = currentSnapshot.cash_balance + additionalFunding;
    let revenue = currentSnapshot.monthly_revenue;
    let expenses = currentSnapshot.monthly_expenses;

    // Add hiring costs
    const avgSalary = 5000; // Average monthly salary
    expenses += additionalHires * avgSalary;

    for (let month = 0; month < months; month++) {
      // Apply growth
      revenue = revenue * (1 + monthlyGrowthRate);

      // Apply price increase (one-time)
      if (month === 0 && priceIncreaseRate > 0) {
        revenue = revenue * (1 + priceIncreaseRate);
      }

      // Calculate cash flow
      const netCashFlow = revenue - expenses;
      cash += netCashFlow;

      projections.push({
        month: month + 1,
        revenue: Math.round(revenue),
        expenses: Math.round(expenses),
        cash: Math.round(cash),
        netCashFlow: Math.round(netCashFlow),
        runway: cash / expenses,
      });

      // Expenses might grow with scale (50% of revenue growth)
      expenses = expenses * (1 + monthlyGrowthRate * 0.5);
    }

    return projections;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading scenarios...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => router.push("/dashboard")}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            <div>
              <h1 className="text-2xl font-bold">Scenario Planning</h1>
              <p className="text-sm text-muted-foreground">
                Model different growth, funding, and operational scenarios
              </p>
            </div>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Scenario
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Scenario</DialogTitle>
                <DialogDescription>
                  Model a business scenario with different parameters
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="name">Scenario Name</Label>
                  <Input
                    id="name"
                    placeholder="e.g., Aggressive Growth"
                    value={scenarioName}
                    onChange={(e) => setScenarioName(e.target.value)}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    placeholder="Brief description of this scenario"
                    value={scenarioDescription}
                    onChange={(e) => setScenarioDescription(e.target.value)}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="growth">Monthly Growth Rate (%)</Label>
                    <Input
                      id="growth"
                      type="number"
                      value={growthRate}
                      onChange={(e) => setGrowthRate(e.target.value)}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="funding">Additional Funding ($)</Label>
                    <Input
                      id="funding"
                      type="number"
                      value={fundingAmount}
                      onChange={(e) => setFundingAmount(e.target.value)}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="months">Months to Simulate</Label>
                    <Input
                      id="months"
                      type="number"
                      value={monthsToSimulate}
                      onChange={(e) => setMonthsToSimulate(e.target.value)}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="price">Price Increase (%)</Label>
                    <Input
                      id="price"
                      type="number"
                      value={priceIncrease}
                      onChange={(e) => setPriceIncrease(e.target.value)}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="hires">New Hires</Label>
                    <Input
                      id="hires"
                      type="number"
                      value={newHires}
                      onChange={(e) => setNewHires(e.target.value)}
                    />
                  </div>
                </div>
                <Button onClick={createScenario} className="w-full">
                  Generate Scenario
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {scenarios.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <p className="text-muted-foreground mb-4">No scenarios yet</p>
              <Button onClick={() => setDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Scenario
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6">
            {/* Scenarios List */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {scenarios.map((scenario) => (
                <Card
                  key={scenario.id}
                  className={`cursor-pointer transition-all ${
                    selectedScenario?.id === scenario.id ? "ring-2 ring-primary" : ""
                  }`}
                  onClick={() => setSelectedScenario(scenario)}
                >
                  <CardHeader>
                    <CardTitle className="text-lg">{scenario.name}</CardTitle>
                    <CardDescription>{scenario.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Growth Rate:</span>
                      <span className="font-medium">{(scenario.growth_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Funding:</span>
                      <span className="font-medium">${(scenario.funding_amount / 1000).toFixed(0)}K</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Duration:</span>
                      <span className="font-medium">{scenario.months_to_simulate} months</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Scenario Details */}
            {selectedScenario && selectedScenario.projections && (
              <div className="grid gap-6">
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Final Cash
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        ${(selectedScenario.projections[selectedScenario.projections.length - 1].cash / 1000).toFixed(0)}K
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Final Revenue
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        ${(selectedScenario.projections[selectedScenario.projections.length - 1].revenue / 1000).toFixed(0)}K
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Final Runway
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {selectedScenario.projections[selectedScenario.projections.length - 1].runway.toFixed(1)} mo
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Total Revenue
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        ${(selectedScenario.projections.reduce((sum: number, p: any) => sum + p.revenue, 0) / 1000).toFixed(0)}K
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Cash Flow */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Cash Position</CardTitle>
                      <CardDescription>Projected cash over time</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={selectedScenario.projections}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="month" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Line type="monotone" dataKey="cash" stroke="#3b82f6" strokeWidth={2} />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  {/* Revenue vs Expenses */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Revenue & Expenses</CardTitle>
                      <CardDescription>Monthly comparison</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={selectedScenario.projections}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="month" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Bar dataKey="revenue" fill="#10b981" />
                          <Bar dataKey="expenses" fill="#ef4444" />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
