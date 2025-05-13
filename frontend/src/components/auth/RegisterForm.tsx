// src/components/auth/RegisterForm.tsx
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { register } from "@/services/auth";
import { useNavigate, Link } from "react-router-dom";

export function RegisterForm({ className, ...props }: React.ComponentPropsWithoutRef<"div">) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(username, email, password);
      navigate("/auth/login");
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred.");
    }
  };

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-xl">Create your account</CardTitle>
          <CardDescription>Sign up with your Instagram or Google account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleRegister}>
            <div className="grid gap-6">
              {error && <div className="text-red-500 text-sm">{error}</div>}
              <div className="flex flex-col gap-4">
                <Button variant="outline" className="w-full" type="button">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M7.5 2h9A5.5 5.5 0 0122 7.5v9a5.5 5.5 0 01-5.5 5.5h-9A5.5 5.5 0 012 16.5v-9A5.5 5.5 0 017.5 2zm9 1.5h-9A4 4 0 003.5 7.5v9a4 4 0 004 4h9a4 4 0 004-4v-9a4 4 0 00-4-4zm-4.5 3A5.5 5.5 0 1017.5 12 5.5 5.5 0 0012 6.5zm0 9A3.5 3.5 0 1115.5 12 3.5 3.5 0 0112 15.5zm5.75-9.5a1.25 1.25 0 11-1.25-1.25A1.25 1.25 0 0117.75 6z"/></svg>
                  Sign up with Instagram
                </Button>
                <Button variant="outline" className="w-full" type="button">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"/></svg>
                  Sign up with Google
                </Button>
              </div>
              <div className="relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t after:border-border">
                <span className="relative z-10 bg-background px-2 text-muted-foreground">Or continue with</span>
              </div>
              <div className="grid gap-6">
                <div className="grid gap-2">
                  <Label htmlFor="username">Username</Label>
                  <Input id="username" type="text" required value={username} onChange={e => setUsername(e.target.value)} placeholder="username" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="m@example.com" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="password">Password</Label>
                  <Input id="password" type="password" required value={password} onChange={e => setPassword(e.target.value)} />
                </div>
                <Button type="submit" className="w-full">Sign up</Button>
              </div>
              <div className="text-center text-sm">
                Already have an account? <Link to="/auth/login" className="underline underline-offset-4">Login</Link>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
      <div className="text-balance text-center text-xs text-muted-foreground [&_a]:underline [&_a]:underline-offset-4 [&_a]:hover:text-primary">
        By clicking continue, you agree to our <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.
      </div>
    </div>
  );
}