"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/lib/supabase";

export default function OnboardingPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    // Company Info
    companyName: "",
    country: "",
    industry: "",
    stage: "seed" as "idea" | "mvp" | "seed" | "series_a" | "series_b" | "growth",
    legalForm: "pvt_ltd" as string,
    teamSize: "",
    // Financial Info
    cashBalance: "",
    monthlyRevenue: "",
    monthlyExpenses: "",
    cac: "",
    ltv: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (step < 2) {
      setStep(step + 1);
      return;
    }

    setLoading(true);

    try {
      // Get current user
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) throw new Error("No user found");

      // Create company
      const { data: company, error: companyError } = await supabase
        .from("companies")
        .insert({
          user_id: user.id,
          name: formData.companyName,
          country: formData.country,
          industry: formData.industry,
          stage: formData.stage,
          legal_form: formData.legalForm,
          team_size: parseInt(formData.teamSize) || null,
        })
        .select()
        .single();

      if (companyError) throw companyError;

      // Create initial financial snapshot
      const { error: financeError } = await supabase.from("financial_snapshots").insert({
        company_id: company.id,
        cash_balance: parseFloat(formData.cashBalance) || null,
        monthly_revenue: parseFloat(formData.monthlyRevenue) || null,
        monthly_expenses: parseFloat(formData.monthlyExpenses) || null,
        cac: parseFloat(formData.cac) || null,
        ltv: parseFloat(formData.ltv) || null,
        burn_rate:
          (parseFloat(formData.monthlyExpenses) || 0) -
          (parseFloat(formData.monthlyRevenue) || 0),
        runway_months:
          parseFloat(formData.cashBalance) && parseFloat(formData.monthlyExpenses)
            ? parseFloat(formData.cashBalance) /
              (parseFloat(formData.monthlyExpenses) - (parseFloat(formData.monthlyRevenue) || 0))
            : null,
      });

      if (financeError) throw financeError;

      toast({
        title: "Success!",
        description: "Your company profile has been created.",
      });

      router.push("/dashboard");
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Something went wrong",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4 py-12">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Let's set up your company profile</CardTitle>
            <CardDescription>
              Step {step} of 2: {step === 1 ? "Company Information" : "Financial Information"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {step === 1 && (
                <>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Company Name *</label>
                    <Input
                      placeholder="Acme Inc."
                      value={formData.companyName}
                      onChange={(e) =>
                        setFormData({ ...formData, companyName: e.target.value })
                      }
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Country *</label>
                      <select
                        className="w-full h-10 rounded-md border border-input bg-background px-3 py-2"
                        value={formData.country}
                        onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                        required
                      >
                        <option value="">Select country</option>
                        <option value="US">United States</option>
                        <option value="IN">India</option>
                        <option value="UK">United Kingdom</option>
                        <option value="SG">Singapore</option>
                        <option value="CA">Canada</option>
                      </select>
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium">Industry *</label>
                      <select
                        className="w-full h-10 rounded-md border border-input bg-background px-3 py-2"
                        value={formData.industry}
                        onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                        required
                      >
                        <option value="">Select industry</option>
                        <option value="SaaS">SaaS</option>
                        <option value="E-commerce">E-commerce</option>
                        <option value="Fintech">Fintech</option>
                        <option value="Healthcare">Healthcare</option>
                        <option value="EdTech">EdTech</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Stage *</label>
                      <select
                        className="w-full h-10 rounded-md border border-input bg-background px-3 py-2"
                        value={formData.stage}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            stage: e.target.value as any,
                          })
                        }
                        required
                      >
                        <option value="idea">Idea</option>
                        <option value="mvp">MVP</option>
                        <option value="seed">Seed</option>
                        <option value="series_a">Series A</option>
                        <option value="series_b">Series B</option>
                        <option value="growth">Growth</option>
                      </select>
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium">Legal Form</label>
                      <select
                        className="w-full h-10 rounded-md border border-input bg-background px-3 py-2"
                        value={formData.legalForm}
                        onChange={(e) => setFormData({ ...formData, legalForm: e.target.value })}
                      >
                        <option value="pvt_ltd">Private Limited</option>
                        <option value="llc">LLC</option>
                        <option value="c_corp">C-Corp</option>
                        <option value="s_corp">S-Corp</option>
                        <option value="llp">LLP</option>
                      </select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Team Size</label>
                    <Input
                      type="number"
                      placeholder="5"
                      value={formData.teamSize}
                      onChange={(e) => setFormData({ ...formData, teamSize: e.target.value })}
                    />
                  </div>
                </>
              )}

              {step === 2 && (
                <>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Cash Balance ($)</label>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="100000"
                      value={formData.cashBalance}
                      onChange={(e) => setFormData({ ...formData, cashBalance: e.target.value })}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Monthly Revenue ($)</label>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="20000"
                        value={formData.monthlyRevenue}
                        onChange={(e) =>
                          setFormData({ ...formData, monthlyRevenue: e.target.value })
                        }
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium">Monthly Expenses ($)</label>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="15000"
                        value={formData.monthlyExpenses}
                        onChange={(e) =>
                          setFormData({ ...formData, monthlyExpenses: e.target.value })
                        }
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">CAC - Customer Acquisition Cost ($)</label>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="500"
                        value={formData.cac}
                        onChange={(e) => setFormData({ ...formData, cac: e.target.value })}
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium">LTV - Lifetime Value ($)</label>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="2000"
                        value={formData.ltv}
                        onChange={(e) => setFormData({ ...formData, ltv: e.target.value })}
                      />
                    </div>
                  </div>

                  <p className="text-sm text-muted-foreground">
                    Don't worry, you can update these numbers anytime from your dashboard.
                  </p>
                </>
              )}

              <div className="flex justify-between pt-4">
                {step > 1 && (
                  <Button type="button" variant="outline" onClick={() => setStep(step - 1)}>
                    Back
                  </Button>
                )}
                <Button type="submit" disabled={loading} className="ml-auto">
                  {loading ? "Saving..." : step === 2 ? "Complete Setup" : "Continue"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
