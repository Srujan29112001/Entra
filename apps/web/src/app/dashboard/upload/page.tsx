"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { supabase } from "@/lib/supabase";
import { useToast } from "@/hooks/use-toast";
import { Upload, FileText, ArrowLeft, Check } from "lucide-react";

export default function UploadPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState<string>("tax");

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);

    try {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) throw new Error("Not authenticated");

      // Get company
      const { data: companies } = await supabase
        .from("companies")
        .select("id")
        .eq("user_id", user.id)
        .limit(1);

      if (!companies || companies.length === 0) throw new Error("No company found");

      const companyId = companies[0].id;

      // Upload file to Supabase Storage
      const fileExt = selectedFile.name.split(".").pop();
      const fileName = `${companyId}/${Date.now()}.${fileExt}`;

      const { error: uploadError, data: uploadData } = await supabase.storage
        .from("documents")
        .upload(fileName, selectedFile);

      if (uploadError) throw uploadError;

      // Get public URL
      const {
        data: { publicUrl },
      } = supabase.storage.from("documents").getPublicUrl(fileName);

      // Create document record
      const { error: dbError } = await supabase.from("documents").insert({
        company_id: companyId,
        user_id: user.id,
        name: selectedFile.name,
        document_type: documentType,
        file_url: publicUrl,
        file_size: selectedFile.size,
        mime_type: selectedFile.type,
        processed: false,
      });

      if (dbError) throw dbError;

      toast({
        title: "Success!",
        description: "File uploaded successfully",
      });

      // Trigger processing
      setProcessing(true);

      // Call backend to process document
      await fetch("http://localhost:8000/api/v1/documents/ingest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          file_url: publicUrl,
          company_id: companyId,
          document_type: documentType,
        }),
      });

      setProcessing(false);

      toast({
        title: "Document Processed",
        description: "Your document is now searchable by AI advisors",
      });

      setSelectedFile(null);
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setUploading(false);
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <Button variant="ghost" onClick={() => router.push("/dashboard")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle>Upload Documents</CardTitle>
            <CardDescription>
              Upload tax documents, contracts, financial statements, or market research for AI analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium">Document Type</label>
              <select
                className="w-full h-10 rounded-md border border-input bg-background px-3 py-2"
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
              >
                <option value="tax">Tax Document</option>
                <option value="legal">Legal/Contract</option>
                <option value="financial">Financial Statement</option>
                <option value="market_research">Market Research</option>
                <option value="pitch_deck">Pitch Deck</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              {!selectedFile ? (
                <>
                  <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-sm text-gray-600 mb-2">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-xs text-gray-500 mb-4">
                    PDF, DOC, DOCX up to 10MB
                  </p>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload">
                    <Button asChild>
                      <span>Select File</span>
                    </Button>
                  </label>
                </>
              ) : (
                <>
                  <FileText className="h-12 w-12 text-primary mx-auto mb-4" />
                  <p className="text-sm font-medium mb-2">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500 mb-4">
                    {(selectedFile.size / 1024).toFixed(2)} KB
                  </p>
                  <div className="flex gap-2 justify-center">
                    <Button onClick={handleUpload} disabled={uploading || processing}>
                      {uploading
                        ? "Uploading..."
                        : processing
                        ? "Processing..."
                        : "Upload & Process"}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setSelectedFile(null)}
                      disabled={uploading || processing}
                    >
                      Cancel
                    </Button>
                  </div>
                </>
              )}
            </div>

            {processing && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900">
                  🤖 AI is processing your document... This may take a moment.
                </p>
              </div>
            )}

            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <p className="text-sm font-medium">What happens after upload?</p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-green-600 mt-0.5" />
                  <span>Document is securely stored</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-green-600 mt-0.5" />
                  <span>AI extracts key information and clauses</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-green-600 mt-0.5" />
                  <span>Content becomes searchable for AI advisors</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-green-600 mt-0.5" />
                  <span>Grounded insights in chat responses</span>
                </li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
