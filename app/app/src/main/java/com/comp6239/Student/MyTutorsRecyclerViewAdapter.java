package com.comp6239.Student;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.comp6239.Backend.Messaging.Message;
import com.comp6239.Backend.Messaging.MessageState;
import com.comp6239.Backend.Messaging.MessageThread;
import com.comp6239.R;

import java.util.List;

/**
 * {@link RecyclerView.Adapter} that can display a {@link} and makes a call to the
 * specified {@link StudentMyTutorsFragment.OnMyTutorsFragmentInteractionListener}.
 * TODO: Replace the implementation with code for your data type.
 */
public class MyTutorsRecyclerViewAdapter extends RecyclerView.Adapter<MyTutorsRecyclerViewAdapter.ViewHolder> {

    private final List<MessageThread> mValues;
    private final StudentMyTutorsFragment.OnMyTutorsFragmentInteractionListener mListener;

    public MyTutorsRecyclerViewAdapter(List<MessageThread> items, StudentMyTutorsFragment.OnMyTutorsFragmentInteractionListener listener) {
        mValues = items;
        mListener = listener;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.conversation_item, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(final ViewHolder holder, int position) {
        holder.mItem = mValues.get(position);
        holder.mNameView.setText(mValues.get(position).getRecipient().getFirstName() + " " + mValues.get(position).getRecipient().getLastName()); //Get name
        holder.mRecentMessageView.setText(mValues.get(position).getMessages()[mValues.get(position).getMessages().length - 1].getMessage()); //Get the last messages text

        Integer unreadMessages = 0;
        for(Message m : mValues.get(position).getMessages()) {
            if(m.getState() == MessageState.DELIVERED ) {
                unreadMessages++;
            }
        }

        holder.mNotifNumberView.setText(unreadMessages.toString());

        holder.mView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (null != mListener) {
                    // Notify the active callbacks interface (the activity, if the
                    // fragment is attached to one) that an item has been selected.
                    mListener.onMyTutorsFragmentInteraction(holder.mItem);
                }
            }
        });
    }

    @Override
    public int getItemCount() {
        if (mValues == null) return 0;
        return mValues.size();
    }

    public class ViewHolder extends RecyclerView.ViewHolder {
        public final View mView;
        public final TextView mNameView;
        public final TextView mRecentMessageView;
        public final TextView mNotifNumberView;
        public MessageThread mItem;

        public ViewHolder(View view) {
            super(view);
            mView = view;
            mNameView = (TextView) view.findViewById(R.id.recipient_name);
            mRecentMessageView = (TextView) view.findViewById(R.id.most_recent_message);
            mNotifNumberView = (TextView) view.findViewById(R.id.notification_number);
        }

        @Override
        public String toString() {
            return super.toString() + " '" + mRecentMessageView.getText() + "'";
        }
    }
}
