/*

gcc -fPIC -DPIC -shared -rdynamic -o sshdauth.so sshdauth.c
cp -fv sshdauth.so /lib/`uname -m`-linux-gnu/security/

vim /etc/pam.d/sshd
auth required sshdauth.so

vim /etc/ssh/sshd_config
UsePAM yes
UsePrivilegeSeparation no
PasswordAuthentication yes
ChallengeResponseAuthentication yes

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <unistd.h>

#include <security/pam_appl.h>
#include <security/pam_modules.h>

int pam_sm_setcred(pam_handle_t *pamh, int flags, int argc, const char *argv[]) { return PAM_SUCCESS; }

int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
	int pame = 0;
	const char *umsg = "Username: ", *pmsg = "Password: ", *cmsg = "Passcode: ";
	const char *user = NULL, *pass = NULL, *code = NULL;
	struct pam_conv *conv;
	struct pam_message mesg;
	struct pam_response *resp;
	const struct pam_message *msgp;
	
	int link[2];
	char data[96], auth[2048];
	pid_t pidn;
	
	/* pam setup */
	
	pame = pam_get_user(pamh, &user, NULL);
	if ((pame != PAM_SUCCESS) || (user == NULL))
	{
		return PAM_AUTH_ERR;
	}
	
	pame = pam_get_authtok(pamh, PAM_AUTHTOK, (const char **)&pass, NULL);
	if (pame != PAM_SUCCESS)
	{
		return PAM_AUTH_ERR;
	}
	
	if (fork() == 0)
	{
		execl("/usr/bin/python", "python", "/opt/freeradius/freeauth.py", "120", user, pass, NULL);
		exit(0);
	}
	
	wait(NULL);
	
	pame = pam_get_item(pamh, PAM_CONV, (const void **)&conv);
	if (pame != PAM_SUCCESS)
	{
		return PAM_AUTH_ERR;
	}
	//mesg.msg_style = PAM_PROMPT_ECHO_OFF;
	mesg.msg_style = PAM_PROMPT_ECHO_ON;
	mesg.msg = cmsg;
	msgp = &mesg;
	
	resp = NULL;
	pame = (*conv->conv)(1, &msgp, &resp, conv->appdata_ptr);
	if ((pame != PAM_SUCCESS) || (resp == NULL))
	{
		return PAM_AUTH_ERR;
	}
	code = resp->resp;
	
	/* auth check */
	
	if (pipe(link) == -1)
	{
		return PAM_AUTH_ERR;
	}
	
	pidn = fork();
	if (pidn == -1)
	{
		return PAM_AUTH_ERR;
	}
	
	if (pidn == 0)
	{
		dup2(link[1], STDOUT_FILENO);
		close(link[0]);
		bzero(auth, 2046 * sizeof(char));
		strncpy(auth, pass, 256);
		strncpy(auth + strlen(auth), code, 256);
		execl("/usr/bin/python", "python", "/opt/freeradius/freeauth.py", "120", user, auth, NULL);
		exit(0);
	}
	
	close(link[1]);
	bzero(data, 94 * sizeof(char));
	read(link[0], data, 92 * sizeof(char));
	wait(NULL);
	
	if (strcmp(data, "Accept") == 0)
	{
		return PAM_SUCCESS;
	}
	
	return PAM_AUTH_ERR;
}
