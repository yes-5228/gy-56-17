import { get, post, put, del } from "./http";

export const travelApi = {
  getAttractions: () => get("/attractions/"),
  getRoutes: () => get("/routes/"),
  getBookings: () => get("/bookings/"),
  getNotices: () => get("/notifications/"),
  createBooking: (payload) => post("/bookings/", payload),
  getTravelers: (bookingId) => get(`/bookings/travelers/?booking=${bookingId}`),
  createTraveler: (payload) => post("/bookings/travelers/", payload),
  updateTraveler: (id, payload) => put(`/bookings/travelers/${id}/`, payload),
  deleteTraveler: (id) => del(`/bookings/travelers/${id}/`),
};
