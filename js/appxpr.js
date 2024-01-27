import ProtonWebSDK from '@proton/web-sdk';

const login = async (restoreSession) => {
    const { link: localLink, session: localSession } = await ProtonWebSDK({
      linkOptions: {
        endpoints,
        chainId,
        restoreSession,
      },
      transportOptions: {
        requestAccount: appIdentifier
      },
      selectorOptions: {
        appName: "Tasklyy",
        appLogo: "https://taskly.protonchain.com/static/media/taskly-logo.ad0bfb0f.svg",
        customStyleOptions: {
            modalBackgroundColor: "#F4F7FA",
            logoBackgroundColor: "white",
            isLogoRound: true,
            optionBackgroundColor: "white",
            optionFontColor: "black",
            primaryFontColor: "black",
            secondaryFontColor: "#6B727F",
            linkColor: "#752EEB"
        }
      }
    })
​
    link = localLink
    session = localSession
}
​
const logout = async () => {
    if (link && session) {
      await link.removeSession(appIdentifier, session.auth, chainId);
    }
    session = undefined;
    link = undefined;
}
​
const transfer = async ({ to, amount }) => {
    if (!session) {
      throw new Error('No Session');
    }
​
    return await session.transact({
      actions: [{
        /**
         * The token contract, precision and symbol for tokens can be seen at protonscan.io/tokens
         */
​
        // Token contract
        account: "eosio.token",
​
        // Action name
        name: "transfer",
        
        // Action parameters
        data: {
          // Sender
          from: session.auth.actor,
​
          // Receiver
          to: to,
​
          // 4 is precision, XPR is symbol
          quantity: `${(+amount).toFixed(4)} XPR`,
​
          // Optional memo
          memo: ""
        },
        authorization: [session.auth]
      }]
    }, {
      broadcast: true
    })
}
​
// Restore on refresh
login(true)