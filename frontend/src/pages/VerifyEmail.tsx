import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import api from "@/lib/axios";

export default function VerifyEmail() {
  const [params] = useSearchParams();

  const email = params.get("email");
  const token = params.get("token");

  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    async function verify() {
      if (!email || !token) {
        setMessage("Invalid verification link.");
        setLoading(false);
        return;
      }

      try {
        const response = await api.post("/auth/verify-email", {
          email,
          token,
        });

        setSuccess(true);
        setMessage(response.data.message);
      } catch (err: any) {
        setSuccess(false);

        setMessage(
          err.response?.data?.error ||
            "Email verification failed."
        );
      } finally {
        setLoading(false);
      }
    }

    verify();
  }, [email, token]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        Verifying...
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto mt-20 text-center">

      <h1 className="text-3xl font-bold mb-6">
        Email Verification
      </h1>

      <p>{message}</p>

      {success && (
        <Link
          to="/login"
          className="mt-6 inline-block bg-blue-600 text-white px-5 py-2 rounded"
        >
          Go to Login
        </Link>
      )}

    </div>
  );
}