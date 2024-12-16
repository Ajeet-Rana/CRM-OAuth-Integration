// slack.js

import { useState, useEffect } from "react";
import { Box, Button, CircularProgress } from "@mui/material";
import axios from "axios";

export const HubSpotIntegration = ({
  user,
  org,
  integrationParams,
  setIntegrationParams,
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  // Function to open OAuth in a new window for HubSpot
  const handleConnectClick = async (event) => {
    event.preventDefault();
    try {
      setIsConnecting(true);
      const formData = new FormData();
      formData.append("user_id", user);
      formData.append("org_id", org);

      // Sending the request to your backend to generate the authorization URL
      const response = await axios.post(
        `http://localhost:8000/integrations/hubspot/authorize`,
        formData
      );
      console.log(response);
      const authURL = response?.data?.url?.raw_headers.find(
        (header) => header[0].toLowerCase() === "location"
      )[1];

      // Open a new window with the HubSpot OAuth authorization URL
      const newWindow = window.open(
        authURL,
        "HubSpot Authorization",
        "width=600, height=600"
      );
      //window.location.href = authURL;
      // Polling for the window to close (OAuth callback)
      const pollTimer = window.setInterval(() => {
        if (newWindow?.closed !== false) {
          window.clearInterval(pollTimer);
          handleWindowClosed();
        }
      }, 200);
    } catch (e) {
      setIsConnecting(false);
      alert(
        e?.response?.data?.detail ||
          "An error occurred while trying to connect to HubSpot."
      );
    } /*
      if (authURL) {
        // Open the authorization URL in a new tab or popup
        window.open(authURL, "HubSpot Authorization", "width=600,height=600");
      }
    } catch (error) {
      console.error("Error during authorization", error);
    }*/
  };

  // Function to handle logic when the OAuth window closes
  const handleWindowClosed = async () => {
    try {
      const formData = new FormData();
      formData.append("user_id", user);
      formData.append("org_id", org);

      // After window is closed, fetch the credentials from the backend
      const response = await axios.post(
        `http://localhost:8000/integrations/hubspot/credentials`,
        formData
      );
      const credentials = response.data;
      console.log(credentials);
      if (credentials) {
        setIsConnecting(false);
        setIsConnected(true);

        // Update the integration parameters in the parent component
        setIntegrationParams((prev) => ({
          ...prev,
          credentials: credentials,
          type: "HubSpot",
        }));
      }
      setIsConnecting(false);
    } catch (e) {
      setIsConnecting(false);
      alert(
        e?.response?.data?.detail ||
          "An error occurred while fetching HubSpot credentials."
      );
    }
  };

  // Check if already connected when the component mounts
  useEffect(() => {
    setIsConnected(integrationParams?.credentials ? true : false);
  }, [integrationParams]);

  return (
    <>
      <Box sx={{ mt: 2 }}>
        Parameters
        <Box
          display="flex"
          alignItems="center"
          justifyContent="center"
          sx={{ mt: 2 }}
        >
          <Button
            variant="contained"
            onClick={isConnected ? () => {} : handleConnectClick}
            color={isConnected ? "success" : "primary"}
            disabled={isConnecting}
            style={{
              pointerEvents: isConnected ? "none" : "auto",
              cursor: isConnected ? "default" : "pointer",
              opacity: isConnected ? 1 : undefined,
            }}
          >
            {isConnected ? (
              "HubSpot Connected"
            ) : isConnecting ? (
              <CircularProgress size={20} />
            ) : (
              "Connect to HubSpot"
            )}
          </Button>
        </Box>
      </Box>
    </>
  );
};
