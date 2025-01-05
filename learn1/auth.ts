import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";

export const {handlers, auth, signIn, signOut} = NextAuth({
    providers: [GitHub],
    callbacks: {
        // async signIn({user, account, profile}) {
        //     console.log("user", user);
        //     console.log("account", account);
        //     console.log("profile", profile);
        //     return true;
        // },
        // async jwt(params) {
        //     console.log(params);
            
        //     return params.token;
        // },

        async session(params) {
            console.log(params);

            return params.session;
        }
        
    }
});