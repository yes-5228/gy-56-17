<template>
  <section class="booking-layout">
    <form class="booking-form" @submit.prevent="submit">
      <div>
        <p class="eyebrow">Registration</p>
        <h3>新增报名</h3>
      </div>
      <label>
        选择线路
        <select v-model.number="form.route" required>
          <option disabled value="">请选择</option>
          <option v-for="route in routes" :key="route.id" :value="route.id">{{ route.title }}</option>
        </select>
      </label>
      <label>
        联系人
        <input v-model="form.contact_name" required />
      </label>
      <label>
        手机号
        <input v-model="form.phone" required />
      </label>
      <div class="form-row">
        <label>
          人数
          <input v-model.number="form.party_size" min="1" type="number" required />
        </label>
        <label>
          出行日期
          <input v-model="form.travel_date" type="date" required />
        </label>
      </div>
      <label>
        备注
        <textarea v-model="form.remark" rows="3"></textarea>
      </label>
      <button class="primary-action" type="submit" :disabled="submittingBooking">
        {{ submittingBooking ? '提交中...' : '提交报名' }}
      </button>
    </form>

    <section class="table-panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Group Status</p>
          <h3>报名与成团状态</h3>
        </div>
        <span>{{ bookings.length }} 条报名</span>
      </div>
      <div class="booking-list">
        <div v-for="booking in bookings" :key="booking.id" class="booking-group">
          <article class="booking-head" @click="toggleExpand(booking.id)">
            <div>
              <h4>{{ booking.contact_name }} · {{ booking.party_size }} 人</h4>
              <p>{{ booking.route_title }} / {{ booking.travel_date }}</p>
            </div>
            <span class="tag">{{ booking.status_label }}</span>
            <strong>{{ booking.group_enrolled }}/{{ booking.min_group_size }}</strong>
            <span class="expand-icon">{{ expandedBooking === booking.id ? '▲' : '▼' }}</span>
          </article>

          <div v-if="expandedBooking === booking.id" class="traveler-section">
            <div class="traveler-head">
              <h5>游客名单（{{ getTravelerCount(booking) }}/{{ booking.party_size }}）</h5>
              <button
                v-if="!isAddingTraveler(booking.id)"
                type="button"
                class="link-button"
                :class="{ disabled: isTravelerFull(booking) }"
                :disabled="isTravelerFull(booking)"
                @click.stop="startAddTraveler(booking)"
              >
                {{ isTravelerFull(booking) ? '人数已满' : '+ 添加游客' }}
              </button>
            </div>

            <div v-if="isAddingTraveler(booking.id)" class="traveler-form-card">
              <div class="traveler-form">
                <label>
                  姓名
                  <input v-model="travelerForm.name" required />
                </label>
                <div class="form-row">
                  <label>
                    证件类型
                    <select v-model="travelerForm.id_type" required>
                      <option value="id_card">身份证</option>
                      <option value="passport">护照</option>
                      <option value="hk_macau">港澳通行证</option>
                      <option value="taiwan">台湾通行证</option>
                      <option value="other">其他</option>
                    </select>
                  </label>
                  <label>
                    证件号码
                    <input v-model="travelerForm.id_number" required />
                  </label>
                </div>
                <div class="form-row">
                  <label>
                    年龄
                    <input v-model.number="travelerForm.age" type="number" min="0" />
                  </label>
                </div>
                <label>
                  特殊需求
                  <textarea v-model="travelerForm.special_requirements" rows="2" placeholder="如：饮食禁忌、轮椅需求等"></textarea>
                </label>
              </div>
              <div class="form-actions">
                <button type="button" class="cancel-button" @click.stop="cancelTravelerForm" :disabled="submittingTraveler">取消</button>
                <button type="button" class="primary-action" @click.stop="submitTraveler(booking.id)" :disabled="submittingTraveler">
                  {{ submittingTraveler ? '处理中...' : (editingTravelerId ? '保存修改' : '确认添加') }}
                </button>
              </div>
            </div>

            <div v-if="booking.travelers && booking.travelers.length > 0" class="traveler-list">
              <div v-for="traveler in booking.travelers" :key="traveler.id" class="traveler-card">
                <div class="traveler-info">
                  <div class="traveler-main">
                    <strong class="traveler-name">{{ traveler.name }}</strong>
                    <span class="tag-tag">{{ traveler.id_type_label }}</span>
                    <span class="traveler-id">{{ traveler.id_number }}</span>
                  </div>
                  <div class="traveler-meta">
                    <span v-if="traveler.age">年龄：{{ traveler.age }}岁</span>
                    <span v-if="traveler.special_requirements" class="special-req">特殊需求：{{ traveler.special_requirements }}</span>
                  </div>
                </div>
                <div class="traveler-actions">
                  <button type="button" class="link-button" @click.stop="startEditTraveler(booking, traveler)" :disabled="deletingTravelerId === traveler.id">编辑</button>
                  <button
                    type="button"
                    class="link-button danger"
                    :class="{ disabled: deletingTravelerId === traveler.id }"
                    :disabled="deletingTravelerId === traveler.id"
                    @click.stop="confirmDeleteTraveler(booking.id, traveler.id)"
                  >
                    {{ deletingTravelerId === traveler.id ? '删除中...' : '删除' }}
                  </button>
                </div>
              </div>
            </div>

            <div v-else-if="!isAddingTraveler(booking.id)" class="empty-travelers">
              暂无游客信息，点击右上角「添加游客」维护名单
            </div>
          </div>
        </div>
      </div>
    </section>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { travelApi } from "../api/travel";

const props = defineProps({
  routes: { type: Array, required: true },
  bookings: { type: Array, required: true },
});

const emit = defineEmits(["data-changed"]);

const form = reactive({
  route: "",
  contact_name: "",
  phone: "",
  party_size: 1,
  travel_date: "",
  status: "pending",
  remark: "",
});

const expandedBooking = ref(null);
const addingBookingId = ref(null);
const editingTravelerId = ref(null);
const submittingBooking = ref(false);
const submittingTraveler = ref(false);
const deletingTravelerId = ref(null);

const travelerForm = reactive({
  name: "",
  id_type: "id_card",
  id_number: "",
  age: null,
  special_requirements: "",
});

function getTravelerCount(booking) {
  return booking.travelers ? booking.travelers.length : 0;
}

function isTravelerFull(booking) {
  return getTravelerCount(booking) >= booking.party_size;
}

function findBookingById(bookingId) {
  return props.bookings.find((b) => b.id === bookingId);
}

function ensureTravelersArray(booking) {
  if (!booking.travelers) {
    booking.travelers = [];
  }
  return booking.travelers;
}

function toggleExpand(bookingId) {
  expandedBooking.value = expandedBooking.value === bookingId ? null : bookingId;
}

function isAddingTraveler(bookingId) {
  return addingBookingId.value === bookingId;
}

function startAddTraveler(booking) {
  if (isTravelerFull(booking)) {
    alert("游客人数已达报名人数上限，无法继续添加");
    return;
  }
  addingBookingId.value = booking.id;
  editingTravelerId.value = null;
  resetTravelerForm();
}

function startEditTraveler(booking, traveler) {
  addingBookingId.value = booking.id;
  editingTravelerId.value = traveler.id;
  travelerForm.name = traveler.name;
  travelerForm.id_type = traveler.id_type;
  travelerForm.id_number = traveler.id_number;
  travelerForm.age = traveler.age;
  travelerForm.special_requirements = traveler.special_requirements || "";
}

function resetTravelerForm() {
  travelerForm.name = "";
  travelerForm.id_type = "id_card";
  travelerForm.id_number = "";
  travelerForm.age = null;
  travelerForm.special_requirements = "";
}

function cancelTravelerForm() {
  addingBookingId.value = null;
  editingTravelerId.value = null;
  resetTravelerForm();
}

function extractErrorMessage(err, fallback) {
  const body = err.body;
  if (body && typeof body === "object") {
    if (body.detail) return body.detail;
    const msgs = Object.values(body).flat().filter(Boolean);
    if (msgs.length) return msgs.join("；");
  }
  if (typeof err.message === "string") {
    try {
      const parsed = JSON.parse(err.message);
      if (parsed && parsed.detail) return parsed.detail;
      if (parsed && typeof parsed === "object") {
        const msgs = Object.values(parsed).flat().filter(Boolean);
        if (msgs.length) return msgs.join("；");
      }
    } catch (_) {
      if (err.message && !err.message.startsWith("{")) return err.message;
    }
  }
  return fallback || "操作失败，请稍后重试";
}

async function submitTraveler(bookingId) {
  if (!travelerForm.name || !travelerForm.id_number) {
    alert("请填写姓名和证件号码");
    return;
  }

  const booking = findBookingById(bookingId);
  if (!editingTravelerId.value && booking && isTravelerFull(booking)) {
    alert("游客人数已达报名人数上限，无法继续添加");
    return;
  }

  const payload = {
    booking: bookingId,
    name: travelerForm.name,
    id_type: travelerForm.id_type,
    id_number: travelerForm.id_number,
    age: travelerForm.age || null,
    special_requirements: travelerForm.special_requirements || "",
  };

  submittingTraveler.value = true;
  try {
    if (editingTravelerId.value) {
      const updated = await travelApi.updateTraveler(editingTravelerId.value, payload);
      if (booking) {
        const travelers = ensureTravelersArray(booking);
        const idx = travelers.findIndex((t) => t.id === editingTravelerId.value);
        if (idx !== -1) {
          travelers.splice(idx, 1, updated);
        }
      }
    } else {
      const created = await travelApi.createTraveler(payload);
      if (booking) {
        const travelers = ensureTravelersArray(booking);
        travelers.push(created);
      }
    }
    cancelTravelerForm();
  } catch (err) {
    alert(`操作失败：${extractErrorMessage(err, "请稍后重试")}`);
  } finally {
    submittingTraveler.value = false;
  }
}

async function confirmDeleteTraveler(bookingId, travelerId) {
  if (!confirm("确定要删除该游客信息吗？")) return;

  deletingTravelerId.value = travelerId;
  try {
    await travelApi.deleteTraveler(travelerId);
    const booking = findBookingById(bookingId);
    if (booking && booking.travelers) {
      const idx = booking.travelers.findIndex((t) => t.id === travelerId);
      if (idx !== -1) {
        booking.travelers.splice(idx, 1);
      }
    }
  } catch (err) {
    alert(`删除失败：${extractErrorMessage(err, "请稍后重试")}`);
  } finally {
    deletingTravelerId.value = null;
  }
}

function resetBookingForm() {
  form.route = "";
  form.contact_name = "";
  form.phone = "";
  form.party_size = 1;
  form.travel_date = "";
  form.status = "pending";
  form.remark = "";
}

async function submit() {
  if (!form.route) {
    alert("请选择线路");
    return;
  }
  submittingBooking.value = true;
  try {
    const payload = {
      route: form.route,
      contact_name: form.contact_name,
      phone: form.phone,
      party_size: form.party_size,
      travel_date: form.travel_date,
      status: form.status,
      remark: form.remark,
    };
    await travelApi.createBooking(payload);
    resetBookingForm();
    emit("data-changed");
  } catch (err) {
    alert(`报名创建失败：${extractErrorMessage(err, "请稍后重试")}`);
  } finally {
    submittingBooking.value = false;
  }
}
</script>

<style scoped>
.booking-group {
  border-bottom: 1px solid #edf2f7;
}

.booking-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 90px 100px 30px;
  gap: 12px;
  align-items: center;
  padding: 14px 0;
  border-top: 1px solid #edf2f7;
  cursor: pointer;
}

.booking-head:hover {
  background: #f8fafc;
}

.expand-icon {
  color: #78909c;
  font-size: 12px;
  text-align: center;
}

.traveler-section {
  padding: 0 0 16px 16px;
  border-left: 3px solid #e7f2ef;
  margin-left: 8px;
}

.traveler-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 12px 0;
}

.traveler-head h5 {
  margin: 0;
  font-size: 14px;
  color: #415063;
}

.link-button {
  background: none;
  border: none;
  color: #0f766e;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.link-button:hover {
  background: #e7f2ef;
}

.link-button.disabled,
.link-button:disabled {
  color: #9fb3c8;
  cursor: not-allowed;
  background: transparent;
}

.link-button.danger {
  color: #b42318;
}

.link-button.danger:hover {
  background: #fef2f2;
}

.traveler-form-card {
  background: #f8fafc;
  border: 1px solid #dce3ea;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.traveler-form {
  display: grid;
  gap: 10px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #dce3ea;
}

.cancel-button {
  border: 1px solid #cdd6df;
  background: white;
  color: #415063;
  border-radius: 8px;
  padding: 0 16px;
  min-height: 40px;
  font-weight: 600;
}

.cancel-button:hover {
  background: #f5f7fa;
}

.cancel-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.traveler-list {
  display: grid;
  gap: 8px;
}

.traveler-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: white;
  border: 1px solid #dce3ea;
  border-radius: 6px;
  padding: 12px;
}

.traveler-info {
  flex: 1;
  display: grid;
  gap: 6px;
}

.traveler-main {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.traveler-name {
  font-size: 15px;
  color: #17202a;
}

.tag-tag {
  border-radius: 4px;
  background: #edf2f7;
  color: #415063;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 600;
}

.traveler-id {
  color: #65717f;
  font-size: 13px;
  font-family: monospace;
}

.traveler-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  color: #65717f;
  font-size: 13px;
}

.special-req {
  color: #9a3412;
}

.traveler-actions {
  display: flex;
  gap: 4px;
}

.empty-travelers {
  padding: 16px;
  text-align: center;
  color: #78909c;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px dashed #dce3ea;
  font-size: 13px;
}

@media (max-width: 900px) {
  .booking-head {
    grid-template-columns: 1fr;
  }

  .expand-icon {
    text-align: right;
  }

  .traveler-card {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
