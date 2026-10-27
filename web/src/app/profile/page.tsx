import { ProfileForm } from "@/components/profile/profile-form";

export default function ProfilePage() {
  return (
    <div className="mx-auto w-full max-w-2xl px-4 py-10">
      <h1 className="text-page font-bold">Hồ sơ cá nhân</h1>
      <div className="mt-8">
        <ProfileForm />
      </div>
    </div>
  );
}
