import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Toaster } from "@/components/ui/sonner"
import { toast } from "sonner"
import { Music, Download, Search, X, Loader2, PlayCircle, FolderArchive } from "lucide-react"

type AppState = "INPUT" | "REVIEW" | "DOWNLOADING" | "COMPLETED"

interface ReviewData {
  title: string
  thumbnail: string | null
  is_playlist: boolean
  items_count: number
}

export default function App() {
  const [appState, setAppState] = useState<AppState>("INPUT")
  const [url, setUrl] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [reviewData, setReviewData] = useState<ReviewData | null>(null)
  
  const [taskId, setTaskId] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)

  const handleReview = async () => {
    if (!url.trim()) {
      toast.error("Tautan tidak boleh kosong")
      return
    }

    setIsLoading(true)
    try {
      const res = await fetch("/api/v1/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      })
      const data = await res.json()

      if (data.is_valid) {
        setReviewData({
          title: data.title || "Unknown Title",
          thumbnail: data.thumbnail,
          is_playlist: data.is_playlist || false,
          items_count: data.items_count || 1
        })
        setAppState("REVIEW")
      } else {
        toast.error(data.error_message || "Tautan tidak valid")
      }
    } catch {
      toast.error("Gagal terhubung ke server backend")
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownload = async () => {
    setIsLoading(true)
    try {
      const res = await fetch("/api/v1/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, is_playlist: reviewData?.is_playlist })
      })
      const data = await res.json()
      
      if (data.task_id) {
        setTaskId(data.task_id)
        setAppState("DOWNLOADING")
        toast.success("Tugas diantrekan!")
        setProgress(15)
      }
    } catch {
      toast.error("Gagal memulai proses unduh")
    } finally {
      setIsLoading(false)
    }
  }

  const triggerFileDownload = (downloadTaskId: string) => {
    const link = document.createElement("a")
    link.href = `/api/v1/stream/${downloadTaskId}`
    link.download = ""
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const resetFlow = () => {
    setAppState("INPUT")
    setUrl("")
    setReviewData(null)
    setTaskId(null)
    setProgress(0)
  }

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>
    if (appState === "DOWNLOADING" && taskId) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`/api/v1/status/${taskId}`)
          if (!res.ok) return
          const data = await res.json()
          
          if (data.status === "DOWNLOADING") setProgress(45)
          else if (data.status === "ZIPPING") setProgress(85)
          else if (data.status === "COMPLETED") {
            setProgress(100)
            setAppState("COMPLETED")
            toast.success("Berhasil! Mengunduh file ke perangkat Anda...")
            triggerFileDownload(taskId)
            clearInterval(interval)
          } else if (data.status === "FAILED") {
            toast.error(`Gagal: ${data.error}`)
            setAppState("REVIEW")
            clearInterval(interval)
          }
        } catch (err) {
          console.error("Polling error", err)
        }
      }, 2000)
    }
    return () => clearInterval(interval)
  }, [appState, taskId])

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-50 flex flex-col items-center justify-center p-4 selection:bg-emerald-500/30 relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-500/10 blur-[150px] rounded-full pointer-events-none" />

      <div className="w-full max-w-xl z-10 space-y-10">
        
        <div className="text-center space-y-3">
          <div className="inline-flex items-center justify-center p-4 bg-neutral-900 border border-neutral-800 rounded-3xl mb-4 shadow-2xl">
            <Music className="w-10 h-10 text-emerald-400" />
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-br from-white to-neutral-500 bg-clip-text text-transparent">
            Streamdown
          </h1>
          <p className="text-neutral-400 text-lg md:text-xl font-medium">
            Unduh lagu & playlist favoritmu dengan kualitas tertinggi.
          </p>
        </div>

        {appState === "INPUT" && (
          <Card className="bg-neutral-900/40 border-neutral-800/80 backdrop-blur-2xl shadow-2xl">
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row gap-3">
                <Input 
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Paste URL Spotify atau YouTube di sini..." 
                  className="h-14 bg-neutral-950 border-neutral-800 text-base focus-visible:ring-emerald-500/50 rounded-xl px-5"
                  onKeyDown={(e) => e.key === "Enter" && handleReview()}
                />
                <Button 
                  onClick={handleReview} 
                  disabled={isLoading}
                  className="h-14 px-8 bg-emerald-500 hover:bg-emerald-600 text-neutral-950 font-bold text-base rounded-xl transition-all hover:scale-105 active:scale-95"
                >
                  {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5 mr-2" />}
                  Review
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {appState !== "INPUT" && reviewData && (
          <Card className="bg-neutral-900/60 border-neutral-800/80 backdrop-blur-2xl shadow-2xl overflow-hidden rounded-2xl">
            <div className="p-2">
              <div className="relative aspect-video w-full bg-neutral-950 rounded-xl overflow-hidden group">
                {reviewData.thumbnail ? (
                  <img src={reviewData.thumbnail} alt={reviewData.title} className="w-full h-full object-cover opacity-70 group-hover:opacity-90 transition-opacity duration-500" />
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center text-neutral-600 bg-neutral-900/50">
                    <FolderArchive className="w-20 h-20 mb-3 opacity-40" />
                    <span className="font-semibold text-lg tracking-wide">Playlist Archive</span>
                  </div>
                )}
                
                <div className="absolute inset-0 bg-gradient-to-t from-neutral-950 via-neutral-950/50 to-transparent flex items-end p-6 md:p-8">
                  <div className="flex gap-5 items-center w-full">
                    <div className="p-4 bg-emerald-500 text-neutral-950 rounded-full shadow-[0_0_30px_rgba(16,185,129,0.3)]">
                      <PlayCircle className="w-8 h-8" />
                    </div>
                    <div className="flex-1 overflow-hidden">
                      <h3 className="text-2xl font-bold line-clamp-1 text-white">{reviewData.title}</h3>
                      <p className="text-emerald-400 font-semibold text-sm mt-1.5 uppercase tracking-wider">
                        {reviewData.is_playlist ? `Playlist • ${reviewData.items_count} Lagu` : 'Single Track'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <CardFooter className="flex flex-col gap-4 p-6 md:p-8 bg-neutral-900/40">
              {appState === "REVIEW" ? (
                <div className="flex flex-col sm:flex-row gap-3 w-full">
                  <Button 
                    variant="outline" 
                    className="flex-1 h-14 border-neutral-700 hover:bg-neutral-800 hover:text-white rounded-xl font-semibold"
                    onClick={() => setAppState("INPUT")}
                  >
                    <X className="w-5 h-5 mr-2" /> Batal
                  </Button>
                  <Button 
                    className="flex-[2] h-14 bg-emerald-500 hover:bg-emerald-600 text-neutral-950 font-bold text-lg rounded-xl shadow-[0_0_40px_rgba(16,185,129,0.2)] transition-all hover:scale-[1.02] active:scale-[0.98]"
                    onClick={handleDownload}
                    disabled={isLoading}
                  >
                    {isLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Download className="w-6 h-6 mr-2" />}
                    Download Sekarang
                  </Button>
                </div>
              ) : (
                <div className="w-full space-y-4 py-2">
                  <div className="flex justify-between text-sm md:text-base font-medium">
                    <span className="text-neutral-300">
                      {progress < 40 ? "Menyambungkan ke Server..." : 
                       progress < 80 ? "Mengunduh Audio Berkualitas Tinggi..." : 
                       progress < 100 ? "Memproses & Menyimpan File..." : "Unduhan Selesai!"}
                    </span>
                    <span className="text-emerald-400 font-bold">{progress}%</span>
                  </div>
                  <Progress value={progress} className="h-3 bg-neutral-950 rounded-full border border-neutral-800" />
                  
                  {appState === "COMPLETED" && (
                    <Button 
                      variant="outline" 
                      className="w-full mt-6 h-14 border-neutral-700 rounded-xl font-semibold hover:bg-neutral-800"
                      onClick={resetFlow}
                    >
                      Unduh Lagu Lainnya
                    </Button>
                  )}
                </div>
              )}
            </CardFooter>
          </Card>
        )}
      </div>
      
      <Toaster theme="dark" position="bottom-center" />
    </main>
  )
}
