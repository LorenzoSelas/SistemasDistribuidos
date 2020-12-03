module Gauntlet {
	exception Unauthorized{}
	exception RoomAlreadyExists{}
	exception RoomNotExists{}
	
	interface Authentication {
		void changePassword(string user, string currentPassHash, string newPassHash) throws Unauthorized;
		string getNewToken(string user, string passwordHash) throws Unauthorized;
		bool isValid(string token);
  };
	interface MapManagement{
		string getRoom();
		void publish(string token, string roomData) throws RoomAlreadyExists;
		void remove(string token, string roomName) throws RoomNotExists;
	}
}
